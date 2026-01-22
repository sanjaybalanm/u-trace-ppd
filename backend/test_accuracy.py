import json
from model.predictor import PPDPredictor
from model.creatinine_predictor import CreatininePPDPredictor

def run_tests():
    print("========================================")
    print("   PPD Model Accuracy/Logic Test")
    print("========================================")
    
    # Initialize Predictors
    base_model = PPDPredictor()
    creat_model = CreatininePPDPredictor()
    
    # Test Data: Diverse Cases
    test_cases = [
        {
            "id": 1,
            "desc": "High Risk: Tyre Worker, Smoker, Low Creatinine",
            "input": {
                "age": 45, "gender": "male", "bmi": 26.0, 
                "occupation": "tyre_worker", "outdoor_hours": 8, 
                "distance_to_main_road": 50, "smoker": True, 
                "creatinine": 0.6 # Low creatinine inflates exposure
            }
        },
        {
            "id": 2,
            "desc": "Low Risk: Student, Healthy, Normal Creatinine",
            "input": {
                "age": 20, "gender": "female", "bmi": 21.0, 
                "occupation": "student", "outdoor_hours": 1, 
                "distance_to_main_road": 500, "smoker": False, 
                "creatinine": 1.2
            }
        },
        {
            "id": 3,
            "desc": "Medium Risk: Driver, High Traffic, High Creatinine",
            "input": {
                "age": 35, "gender": "male", "bmi": 28.0, 
                "occupation": "driver", "outdoor_hours": 10, 
                "distance_to_main_road": 10, "smoker": False, 
                "creatinine": 1.9 # High creatinine dilutes exposure
            }
        },
        {
            "id": 4,
            "desc": "Extreme Risk: Painter, Smoker, 2-Wheeler, Low Creatinine",
            "input": {
                "age": 50, "gender": "male", "bmi": 24.0, 
                "occupation": "painter", "outdoor_hours": 12, 
                "distance_to_main_road": 50, "smoker": True, "two_wheeler_use": True,
                "creatinine": 0.5
            }
        },
        {
            "id": 5,
            "desc": "Edge Case: Missing Optional Fields",
            "input": {
                "occupation": "office_worker",
                "creatinine": 1.0
            }
        }
    ]
    
    print(f"{'ID':<4} | {'Description':<50} | {'Mode':<10} | {'Score/Val':<10} | {'Risk':<10}")
    print("-" * 100)
    
    for case in test_cases:
        data = case["input"]
        
        # 1. Test Base Model
        score, _ = base_model.predict_score(data)
        print(f"{case['id']:<4} | {case['desc']:<50} | {'Base':<10} | {score:<10} | {'-'}")
        
        # 2. Test Creatinine Model
        res = creat_model.predict_with_creatinine(data)
        print(f"{'':<4} | {'':<50} | {'Creatinine':<10} | {res['normalized_ppd']:<10} | {res['risk_level']:<10}")
        print("-" * 100)

if __name__ == "__main__":
    run_tests()
