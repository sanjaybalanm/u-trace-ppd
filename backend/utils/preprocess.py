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
            "creatinine": float(data.get("creatinine", 1.0))  # Add creatinine support
        }
        
        return processed_data
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None
