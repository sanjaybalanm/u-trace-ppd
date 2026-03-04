from predictor import PPDPredictor

def test_v2_model():
    print("Initializing Predictor...")
    predictor = PPDPredictor()
    
    # Test Case 1: Healthy Person (Should be Low Risk)
    data_healthy = {
        "age": 25, "gender": "female", "occupation": "student",
        "outdoor_hours": 2, "distance_to_main_road": 200, "smoker": False,
        "respiratory_symptoms": False, "skin_allergy_history": False,
        "ige_level": 50, "eosinophil_percentage": 2, "fev1": 95, "patch_test": 0
    }
    
    score1, details1 = predictor.predict_score(data_healthy)
    print(f"\nTest 1 (Healthy): Score={score1}, Label={details1.get('prediction_label')}")
    print(f"Algorithm: {details1['calculation_method']}")
    
    # Test Case 2: Clinical High Risk (Strong Patch Test)
    data_high = {
        "age": 45, "gender": "male", "occupation": "office_worker", # Low risk occ
        "outdoor_hours": 1, "distance_to_main_road": 500, "smoker": False,
        "respiratory_symptoms": True, "skin_allergy_history": True,
        "ige_level": 50, "eosinophil_percentage": 2, "fev1": 95, 
        "patch_test": 2 # STRONG POSITIVE -> Should trigger High Risk
    }
    
    score2, details2 = predictor.predict_score(data_high)
    print(f"\nTest 2 (Clinical High - Patch Test): Score={score2}, Label={details2.get('prediction_label')}")
    print(f"Factors: {details2['key_factors']}")

    # Test Case 3: Respiratory High Risk (Low FEV1)
    data_resp = {
        "age": 55, "gender": "male", "occupation": "driver",
        "outdoor_hours": 8, "distance_to_main_road": 50, "smoker": True,
        "respiratory_symptoms": True, 
        "ige_level": 400, "eosinophil_percentage": 9, "fev1": 50, "patch_test": 0
    }
     
    score3, details3 = predictor.predict_score(data_resp)
    print(f"\nTest 3 (Respiratory High): Score={score3}, Label={details3.get('prediction_label')}")

if __name__ == "__main__":
    test_v2_model()
