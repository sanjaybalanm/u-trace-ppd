from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from utils.preprocess import preprocess_input
from utils.report_generator import generate_pdf_report
from model.predictor import PPDPredictor
from model.risk_classifier import classify_risk
from model.creatinine_predictor import CreatininePPDPredictor
import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import io

app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for frontend

# Initialize predictors
predictor = PPDPredictor()
creatinine_predictor = CreatininePPDPredictor()

def init_db():
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        # Users Table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
        
        # Predictions History Table
        c.execute('''CREATE TABLE IF NOT EXISTS predictions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user_id INTEGER, 
                      date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      risk_level TEXT,
                      score REAL,
                      details TEXT)''') # details stored as JSON string
                      
        conn.commit()
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

init_db()

def save_prediction(user_id, risk_level, score, details):
    """Helper to save prediction to DB"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO predictions (user_id, risk_level, score, details) VALUES (?, ?, ?, ?)",
                  (user_id, risk_level, score, json.dumps(details)))
        conn.commit()
    except Exception as e:
        print(f"Error saving prediction: {e}")
    finally:
        if conn: conn.close()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    hashed_password = generate_password_hash(password)
    
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = None
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

    if user and check_password_hash(user[1], password):
        # Return user ID and Username
        # user tuple from SELECT id, password FROM users... wait, I need username in select
        return jsonify({"message": "Login successful", "user_id": user[0], "username": username}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/predict', methods=['POST'])
def predict():
    """
    API Endpoint to predict PPD exposure risk.
    Expects JSON input with user demographics and habits.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        # 1. Preprocess Input
        processed_data = preprocess_input(data)
        if not processed_data:
            return jsonify({"error": "Invalid input data format"}), 400
            
        # 2. Run Prediction Model
        exposure_score, details = predictor.predict_score(processed_data)
        
        # 3. Classify Risk
        risk_level = classify_risk(exposure_score)
        
        # 4. Construct Response
        response = {
            "predicted_risk": risk_level,
            "exposure_score": exposure_score,
            "key_factors": details.get("key_factors", []),
            "factor_details": details.get("factor_details", []),
            "total_factors_analyzed": details.get("total_factors_analyzed", 5),
            "mode": "STANDARD"
        }
        
        # 5. Save History (if user_id provided)
        user_id = data.get('user_id', 1) # Default to 1 for demo if missing
        save_prediction(user_id, risk_level, exposure_score, response)
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict-with-creatinine', methods=['POST'])
def predict_with_creatinine():
    """
    API Endpoint to predict PPD exposure risk WITH creatinine.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        # 1. Preprocess Input (shared preprocessing)
        processed_data = preprocess_input(data)
        if not processed_data:
            return jsonify({"error": "Invalid input data format"}), 400
            
        # 2. Run Prediction Model
        result = creatinine_predictor.predict_with_creatinine(processed_data)
        
        # 3. Save History
        user_id = data.get('user_id', 1) 
        save_prediction(user_id, result['predicted_risk'], result['normalized_ppd'], result)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """
    Get prediction history for a specific user.
    Query param: user_id
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
        
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Get last 20 predictions
        c.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY date DESC LIMIT 20", (user_id,))
        rows = c.fetchall()
        
        history = []
        for row in rows:
            history.append({
                "id": row['id'],
                "date": row['date'],
                "risk_level": row['risk_level'],
                "score": row['score'],
                "details": json.loads(row['details']) if row['details'] else {}
            })
            
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@app.route('/download-report', methods=['POST'])
def download_report():
    """
    Generate PDF report from prediction data.
    """
    data = request.json
    user_name = data.get('user_name', 'Patient')
    risk_data = data.get('risk_data', {})
    
    try:
        pdf_bytes = generate_pdf_report(user_name, risk_data)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'ppd_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """
    Simple AI Chatbot Endpoint.
    Uses keyword matching to answer common PPD questions.
    """
    try:
        data = request.json
        message = data.get('message', '').lower()
        
        if not message:
             return jsonify({"response": "I didn't catch that. Could you say it again?"}), 400

        # Knowledge Base
        responses = {
            "ppd": "PPD (Paraphenylenediamine) is a chemical commonly found in hair dyes, rubber chemicals, and temporary tattoos. It can cause severe allergic reactions and skin sensitization.",
            "risk": "Risk is calculated based on occupation, smoking habits, traffic proximity, and other factors. High risk means you have significant exposure to PPD sources.",
            "creatinine": "Creatinine is a waste product filtered by kidneys. High levels can indicate kidney stress. In our context, we use it to normalize PPD concentration in urine.",
            "prevent": "To prevent exposure: wear protective gloves, avoid direct skin contact with dyes/rubber, wash hands frequently, and limit time in high-traffic or industrial areas.",
            "symptom": "Common symptoms of PPD exposure include skin irritation, redness, swelling, itching, and in severe cases, respiratory issues.",
            "safe": "A 'Low Risk' score means your exposure is within manageable limits. However, always follow safety guidelines!",
            "hello": "Hello! I'm your PPD Safety Assistant. Ask me about PPD risks, prevention, or your health score.",
            "hi": "Hi there! How can I help you regarding PPD safety today?",
            "thanks": "You're welcome! Stay safe.",
            "bye": "Goodbye! Take care of your health."
        }
        
        # Simple Keyword Matching
        response_text = "I'm not sure about that. Try asking about 'PPD', 'Risk Factors', 'Prevention', or 'Creatinine'."
        
        for key, reply in responses.items():
            if key in message:
                response_text = reply
                break
                
        return jsonify({"response": response_text}), 200

    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting PPD Risk Prediction Backend...")
    app.run(debug=True, port=5001)
