import numpy as np

class PPDPredictor:
    """
    Mock ML Predictor for PPD Exposure Risk.
    Uses heuristic scoring since real lab data is not available.
    """
    
    def __init__(self):
        # Weights for different factors (Mock weights)
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
        Calculates an exposure score based on input features.
        
        Args:
            data (dict): Preprocessed input data.
            
        Returns:
            float: Exposure score between 0.0 and 1.0.
            list: List of key contributing factors.
        """
        score = 0.0
        factors = []
        
        # 1. Occupation Factor (High impact)
        # ---------------------------------------------------------
        occupation = data.get("occupation", "other")
        occ_score = self.occupation_weights.get(occupation, 0.1)
        score += occ_score
        
        if occ_score > 0.2:
            factors.append("High Risk Occupation")
            
        # 2. Outdoor Exposure Factor (Time spent outdoors)
        # ---------------------------------------------------------
        outdoor_hours = data.get("outdoor_hours", 0)
        outdoor_score = min(outdoor_hours / 24.0, 0.2) # Max contribution 0.2
        score += outdoor_score
        
        if outdoor_hours > 6:
            factors.append("Extended Outdoor Duration")
            
        # 3. Traffic Exposure (Distance to road)
        # ---------------------------------------------------------
        distance = data.get("distance_to_main_road", 100)
        # Closer distance = Higher risk. Normalize: 0m -> 0.2, 200m+ -> 0.0
        dist_score = max(0, (200 - distance) / 1000.0) 
        score += dist_score
        
        if distance < 50:
            factors.append("Proximity to Traffic")
            
        # 4. Lifestyle Factors
        # ---------------------------------------------------------
        if data.get("smoker"):
            score += 0.15
            factors.append("Smoking History")
            
        if data.get("two_wheeler_use"):
            score += 0.1
            factors.append("Frequent Two-Wheeler Use")
            
        # Normalize score to 0.0 - 1.0 range (Clamping)
        final_score = min(max(score, 0.0), 1.0)
        
        return round(final_score, 2), factors
