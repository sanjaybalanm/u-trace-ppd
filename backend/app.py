from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.preprocess import preprocess_input
from model.predictor import PPDPredictor
from model.risk_classifier import classify_risk

app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for frontend

# Initialize predictor
predictor = PPDPredictor()

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
    app.run(debug=True, port=5000)
