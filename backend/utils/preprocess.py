import pandas as pd
import numpy as np

def preprocess_input(data):
    """
    Preprocesses the input data for the prediction model.
    
    Args:
        data (dict): Dictionary containing user input.
        
    Returns:
        dict: Processed data dictionary with converted types.
    """
    try:
        # Validate and convert inputs
        processed_data = {
            "age": int(data.get("age", 0)),
            "gender": str(data.get("gender", "")).lower(),
            "bmi": float(data.get("bmi", 0.0)),
            "occupation": str(data.get("occupation", "")).lower(),
            "outdoor_hours": float(data.get("outdoor_hours", 0.0)),
            "distance_to_main_road": float(data.get("distance_to_main_road", 0.0)),
            "two_wheeler_use": bool(data.get("two_wheeler_use", False)),
            "smoker": bool(data.get("smoker", False)),
            "creatinine": float(data.get("creatinine") or 1.0),
            
            # New Clinical Features for v2 Model
            "respiratory_symptoms": bool(data.get("respiratory_symptoms", False)),
            "skin_allergy_history": bool(data.get("skin_allergy_history", False)),
            "ige_level": float(data.get("ige_level") or 0.0),
            "eosinophil_percentage": float(data.get("eosinophil_percentage") or 0.0),
            "fev1": float(data.get("fev1") or 0.0), 
            "patch_test": data.get("patch_test", "0") # Keep as string or int depending on usage, predictor handles both? predictor does int(data.get(...))
        }
        
        return processed_data
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None
