import numpy as np
import pandas as pd
import joblib
import os

class PPDPredictor:
    """
    Hybrid Predictor (v2):
    - Uses 'ppd_risk_model_v2.pkl' (Random Forest with Clinical Features).
    - Uses Heuristic Rules for the 'Explanation'.
    """
    
    def __init__(self):
        # Path setup
        base_dir = os.path.dirname(__file__)
        self.model_path = os.path.join(base_dir, 'ppd_risk_model_v2.pkl')
        self.enc_gender_path = os.path.join(base_dir, 'encoder_gender_v2.pkl')
        self.enc_occ_path = os.path.join(base_dir, 'encoder_occupation_v2.pkl')
        
        self.model = None
        self.le_gender = None
        self.le_occ = None
        
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.le_gender = joblib.load(self.enc_gender_path)
                self.le_occ = joblib.load(self.enc_occ_path)
                print(f"✅ ML Model v2 loaded successfully.")
            else:
                print(f"⚠️ Model v2 not found at {self.model_path}. Using fallback rules.")
        except Exception as e:
            print(f"⚠️ Failed to load ML Model v2: {e}")

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
        Calculates exposure score using ML Model v2.
        """
        score = 0.0
        factors = []
        factor_details = []
        
        # ------------------------------------------------------------
        # 1. GENERATE EXPLANATIONS (Rule-Based for UI Clarity)
        # ------------------------------------------------------------
        
        # [Occupation]
        occupation = data.get("occupation", "other")
        occ_score = self.occupation_weights.get(occupation.lower(), 0.1)
        score += occ_score 
        
        occupation_labels = {
            "tyre_worker": "Tyre Manufacturing Worker",
            "mechanic": "Automotive Mechanic",
            "painter": "Industrial Painter",
            "driver": "Professional Driver",
            "student": "Student",
            "office_worker": "Office Worker",
            "doctor": "Healthcare Professional",
            "farmer": "Agricultural Worker",
            "teacher": "Teacher",
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
        
        # [Clinical Factors - Detailed Analysis]
        ige = float(data.get("ige_level") or 0)
        eos = float(data.get("eosinophil_percentage") or 0)
        fev1 = float(data.get("fev1") or 0)
        patch = int(data.get("patch_test", 0))

        if ige > 0:
            risk = "High" if ige > 300 else "Medium" if ige > 100 else "Low"
            factors.append(f"IgE Level: {ige} IU/mL")
            factor_details.append({
                "name": "Serum IgE Level",
                "value": f"{ige} IU/mL",
                "contribution": 100 if risk == "High" else 50 if risk == "Medium" else 0,
                "risk_level": risk,
                "description": "High IgE indicates strong allergic sensitization." if risk == "High" else "Normal range."
            })

        if eos > 0:
            risk = "High" if eos > 7 else "Medium" if eos > 4 else "Low"
            factors.append(f"Eosinophils: {eos}%")
            factor_details.append({
                "name": "Eosinophil Count",
                "value": f"{eos}%",
                "contribution": 100 if risk == "High" else 50 if risk == "Medium" else 0,
                "risk_level": risk,
                "description": "Elevated eosinophils suggest active allergic inflammation." if risk == "High" else "Normal range."
            })

        if fev1 > 0:
            risk = "High" if fev1 < 60 else "Medium" if fev1 < 80 else "Low"
            factors.append(f"FEV1: {fev1}%")
            factor_details.append({
                "name": "Spirometry (FEV1)",
                "value": f"{fev1}% predicted",
                "contribution": 100 if risk == "High" else 50 if risk == "Medium" else 0,
                "risk_level": risk,
                "description": "Reduced lung function detected." if risk == "High" else "Lung function within normal limits."
            })

        if patch > 0:
            risk = "High" if patch == 2 else "Medium"
            factors.append("Positive Patch Test")
            factor_details.append({
                "name": "Skin Patch Test",
                "value": "Strong Positive (++)" if patch == 2 else "Weak Positive (+)",
                "contribution": 100 if risk == "High" else 50,
                "risk_level": risk,
                "description": "Direct sensitization to PPD confirmed."
            })

        # ------------------------------------------------------------
        # 2. APPLY ML MODEL v2 (Random Forest)
        # ------------------------------------------------------------
        prediction_label = "Low" # Default

        if self.model:
            try:
                # Prepare Input Vector
                # Feature Order: ['Age', 'Gender', 'Occupation', 'Outdoor_Hours', 'Distance_to_Road', 
                #                 'Smoker', 'Two_Wheeler', 'Respiratory_Symptoms', 'Skin_Allergy_History', 
                #                 'IgE_Level', 'Eosinophil_Percentage', 'FEV1', 'Patch_Test']
                
                # Handling Encoders with 'unknown' fallback
                gender_input = data.get('gender', 'Male').title()
                try:
                    gender_enc = self.le_gender.transform([gender_input])[0]
                except:
                    gender_enc = 0 # Default

                occ_input = occupation.replace('_', ' ').title()
                # Map specific frontend values to training values if needed, or rely on training data coverage
                # The training script used: Student, Tyre Worker, Mechanic, Painter, Driver, Office Worker, Other, Doctor, Farmer, Teacher.
                # Frontend sends: student, tyre_worker, etc.
                occ_map = {
                    "student": "Student", "tyre_worker": "Tyre Worker", "mechanic": "Mechanic",
                    "painter": "Painter", "driver": "Driver", "office_worker": "Office Worker",
                    "other": "Other", "doctor": "Doctor", "farmer": "Farmer", "teacher": "Teacher",
                    "construction_worker": "Other", "engineer": "Other", "sales": "Other"
                }
                occ_clean = occ_map.get(occupation, "Other")
                
                try:
                    occ_enc = self.le_occ.transform([occ_clean])[0]
                except:
                    occ_enc = self.le_occ.transform(['Other'])[0]

                # Booleans
                smoker_val = 1 if (str(data.get('smoker')).lower() == 'true') else 0
                two_wheeler_val = 1 if (str(data.get('two_wheeler_use')).lower() == 'true') else 0
                resp_val = 1 if (str(data.get('respiratory_symptoms')).lower() == 'true') else 0
                allergy_val = 1 if (str(data.get('skin_allergy_history')).lower() == 'true') else 0
                
                # Clinical Defaults (if missing) -> Normal values
                ige_val = float(data.get('ige_level') or 50.0) 
                eos_val = float(data.get('eosinophil_percentage') or 2.0)
                fev1_val = float(data.get('fev1') or 95.0)
                patch_val = int(data.get('patch_test', 0))

                input_vector = pd.DataFrame([{
                    'Age': int(data.get('age', 30)),
                    'Gender': gender_enc,
                    'Occupation': occ_enc,
                    'Outdoor_Hours': int(data.get("outdoor_hours", 0)),
                    'Distance_to_Road': int(data.get("distance_to_main_road", 100)),
                    'Smoker': smoker_val,
                    'Two_Wheeler': two_wheeler_val,
                    'Respiratory_Symptoms': resp_val,
                    'Skin_Allergy_History': allergy_val,
                    'IgE_Level': ige_val,
                    'Eosinophil_Percentage': eos_val,
                    'FEV1': fev1_val,
                    'Patch_Test': patch_val
                }])
                
                # Predict
                prediction_label = self.model.predict(input_vector)[0]
                # Probability for 'High' or 'Medium' to create a numeric score?
                # The model outputs 'High', 'Medium', 'Low'.
                # We need a numeric score 0.0 - 1.0 for the UI.
                
                probs = self.model.predict_proba(input_vector)[0]
                classes = self.model.classes_ # ['High', 'Low', 'Medium'] sorted usually?
                
                # Map probs to a single 0-1 score
                # 0 = Low, 0.5 = Medium, 1.0 = High
                # Let's verify class order:
                # usually alphabetical: High, Low, Medium
                
                score_map = {cls: i for i, cls in enumerate(classes)}
                # Calculate weighted score: P(High)*1.0 + P(Medium)*0.5 + P(Low)*0.0
                
                high_idx = score_map.get('High')
                med_idx = score_map.get('Medium')
                
                p_high = probs[high_idx] if high_idx is not None else 0
                p_med = probs[med_idx] if med_idx is not None else 0
                
                final_score = (p_high * 1.0) + (p_med * 0.5)
                
            except Exception as e:
                print(f"⚠️ ML Prediction Error: {e}")
                final_score = min(max(score, 0.0), 1.0) # Fallback to rule score
        else:
            final_score = min(max(score, 0.0), 1.0) # Fallback to rule score
        
        return round(final_score, 2), {
            "key_factors": factors,
            "factor_details": factor_details,
            "total_factors_analyzed": 13,
            "calculation_method": "Clinical ML Model v2" if self.model else "Heuristic Rule System",
            "prediction_label": prediction_label
        }
