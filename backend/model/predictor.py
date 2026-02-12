import numpy as np
import pandas as pd
import joblib
import os

class PPDPredictor:
    """
    Hybrid Predictor:
    - Uses 'ppd_risk_model.pkl' (Random Forest) for the core Risk Score.
    - Uses Heuristic Rules for the 'Explanation' (Factor Details) since the model is a black-box.
    """
    
    def __init__(self):
        # Try to load the trained ML model
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'ppd_risk_model.pkl')
        
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"✅ ML Model loaded from: {self.model_path}")
            except Exception as e:
                print(f"⚠️ Failed to load ML Model: {e}")
        else:
            print(f"⚠️ Model file not found at {self.model_path}. Using fallback rules.")

        # Weights for explanation generation (fallback & UI text)
        self.occupation_weights = {
            "tyre_worker": 0.4,
            "mechanic": 0.35,
            "painter": 0.3,
            "driver": 0.25,
            "student": 0.05,
            "office_worker": 0.1,
            "other": 0.1
        }
        
    def predict_score(self, data):
        """
        Calculates exposure score using ML Model (if available) or Rules.
        """
        score = 0.0
        factors = []
        factor_details = []
        
        # ------------------------------------------------------------
        # 1. GENERATE EXPLANATIONS (Rule-Based for UI Clarity)
        # ------------------------------------------------------------
        # We process the rules primarily to generate the text explanations
        # that the frontend needs. The final SCORE will come from the ML model.
        
        # [Occupation]
        occupation = data.get("occupation", "other")
        occ_score = self.occupation_weights.get(occupation, 0.1)
        score += occ_score # Accumulate for fallback score
        
        occupation_labels = {
            "tyre_worker": "Tyre Manufacturing Worker",
            "mechanic": "Automotive Mechanic",
            "painter": "Industrial Painter",
            "driver": "Professional Driver",
            "student": "Student",
            "office_worker": "Office Worker",
            "other": "Other Occupation"
        }
        
        occ_percentage = round(occ_score * 100, 1)
        risk_level = "High" if occ_score > 0.25 else "Medium" if occ_score > 0.15 else "Low"
        
        factor_details.append({
            "name": "Occupational Exposure",
            "value": occupation_labels.get(occupation, occupation.replace("_", " ").title()),
            "contribution": occ_percentage,
            "risk_level": risk_level,
            "description": f"Your occupation contributes {occ_percentage}% to overall exposure risk."
        })
        
        if occ_score > 0.2:
            factors.append("High Risk Occupation")
            
        # [Outdoor]
        outdoor_hours = data.get("outdoor_hours", 0)
        outdoor_score = min(outdoor_hours / 24.0, 0.2)
        score += outdoor_score
        
        outdoor_risk = "High" if outdoor_hours > 8 else "Medium" if outdoor_hours > 4 else "Low"
        factor_details.append({
            "name": "Outdoor Duration",
            "value": f"{outdoor_hours} hours/day",
            "contribution": round(outdoor_score * 100, 1),
            "risk_level": outdoor_risk,
            "description": f"Spending {outdoor_hours} hours outdoors daily increases exposure."
        })
        if outdoor_hours > 6: factors.append("Extended Outdoor Duration")
            
        # [Traffic]
        distance = data.get("distance_to_main_road", 100)
        dist_score = max(0, (200 - distance) / 1000.0) 
        score += dist_score
        
        traffic_risk = "High" if distance < 50 else "Medium" if distance < 150 else "Low"
        factor_details.append({
            "name": "Traffic Proximity",
            "value": f"{distance} meters",
            "contribution": round(dist_score * 100, 1),
            "risk_level": traffic_risk,
            "description": f"Living {distance}m from main road contributes to exposure."
        })
        if distance < 50: factors.append("Proximity to Traffic")
            
        # [Smoker]
        smoker = data.get("smoker", False)
        if isinstance(smoker, str): smoker = (smoker.lower() == 'true') # strengthen boolean parsing
        smoking_score = 0.15 if smoker else 0.0
        score += smoking_score
        
        factor_details.append({
            "name": "Smoking Status",
            "value": "Yes - Active Smoker" if smoker else "No",
            "contribution": round(smoking_score * 100, 1),
            "risk_level": "High" if smoker else "Low",
            "description": "Smoking significantly increases PPD absorption." if smoker else "Non-smoking reduces risk."
        })
        if smoker: factors.append("Smoking History")
            
        # [Two Wheeler]
        two_wheeler = data.get("two_wheeler_use", False)
        if isinstance(two_wheeler, str): two_wheeler = (two_wheeler.lower() == 'true')
        vehicle_score = 0.1 if two_wheeler else 0.0
        score += vehicle_score
        
        factor_details.append({
            "name": "Two-Wheeler Usage",
            "value": "Regular User" if two_wheeler else "No",
            "contribution": round(vehicle_score * 100, 1),
            "risk_level": "Medium" if two_wheeler else "Low",
            "description": "Regular two-wheeler use increases direct exposure." if two_wheeler else "No additional vehicular exposure."
        })
        if two_wheeler: factors.append("Frequent Two-Wheeler Use")

        # Fallback Rule Calculation (Clamped)
        rule_based_score = min(max(score, 0.0), 1.0)

        # ------------------------------------------------------------
        # 2. APPLY ML MODEL (If Available)
        # ------------------------------------------------------------
        final_score = rule_based_score # Default to rules
        
        if self.model:
            try:
                # Prepare DataFrame matching training columns
                # ['age', 'gender', 'occupation', 'outdoor_hours', 'distance_to_main_road', 'smoker', 'two_wheeler_use', 'creatinine']
                
                # Default creatinine to 1.0 (Average) if using Standard Mode (which lacks creatinine input)
                creatinine_val = float(data.get("creatinine", 1.0))
                
                input_df = pd.DataFrame([{
                    'age': int(data.get('age', 30)),
                    'gender': data.get('gender', 'male'),
                    'occupation': occupation,
                    'outdoor_hours': int(outdoor_hours),
                    'distance_to_main_road': int(distance),
                    'smoker': smoker,
                    'two_wheeler_use': two_wheeler,
                    'creatinine': creatinine_val
                }])
                
                # Predict
                prediction = self.model.predict(input_df)[0]
                
                # ML models can sometimes predict slightly outside 0-1 range due to regression, clamp it.
                final_score = min(max(prediction, 0.0), 1.0)
                
            except Exception as e:
                print(f"⚠️ ML Prediction Error: {e}")
                # Fallback to rule_based_score handled by initialization above
        
        return round(final_score, 2), {
            "key_factors": factors,
            "factor_details": factor_details,
            "total_factors_analyzed": 5,
            "calculation_method": "Random Forest ML Model" if self.model else "Heuristic Rule System"
        }
