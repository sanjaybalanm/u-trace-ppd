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
        }
    ]
    
    print("ID   | Description                                      | Method Used               | Score")
    print("-----|--------------------------------------------------|---------------------------|-------")
    
    for case in test_cases:
        data = case["input"]
        
        # 1. Test Base Model
        score, details = base_model.predict_score(data)
        method = details.get('calculation_method', 'Unknown')
        print(f"{case['id']:<4} | {case['desc'][:48]:<48} | {method:<25} | {score}")
        
    print("\nIf 'Method Used' says 'Random Forest ML Model', then it is working!")

if __name__ == "__main__":
    run_tests()
