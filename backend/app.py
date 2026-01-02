from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.preprocess import preprocess_input
from model.predictor import PPDPredictor
from model.risk_classifier import classify_risk

app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for frontend

# Initialize predictor
predictor = PPDPredictor()

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User created successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        return jsonify({"message": "Login successful"}), 200
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
        exposure_score, key_factors = predictor.predict_score(processed_data)
        
        # 3. Classify Risk
        risk_level = classify_risk(exposure_score)
        
        # 4. Construct Response
        response = {
            "predicted_risk": risk_level,
            "exposure_score": exposure_score,
            "key_factors": key_factors
        }
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting PPD Risk Prediction Backend...")
    app.run(debug=True, port=5001)
