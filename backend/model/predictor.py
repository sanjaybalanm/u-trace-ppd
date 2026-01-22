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
            dict: Detailed breakdown of all factors and contributions.
        """
        score = 0.0
        factors = []
        factor_details = []
        
        # 1. Occupation Factor (High impact)
        # ---------------------------------------------------------
        occupation = data.get("occupation", "other")
        occ_score = self.occupation_weights.get(occupation, 0.1)
        score += occ_score
        
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
            
        # 2. Outdoor Exposure Factor (Time spent outdoors)
        # ---------------------------------------------------------
        outdoor_hours = data.get("outdoor_hours", 0)
        outdoor_score = min(outdoor_hours / 24.0, 0.2) # Max contribution 0.2
        score += outdoor_score
        
        outdoor_percentage = round(outdoor_score * 100, 1)
        outdoor_risk = "High" if outdoor_hours > 8 else "Medium" if outdoor_hours > 4 else "Low"
        
        factor_details.append({
            "name": "Outdoor Duration",
            "value": f"{outdoor_hours} hours/day",
            "contribution": outdoor_percentage,
            "risk_level": outdoor_risk,
            "description": f"Spending {outdoor_hours} hours outdoors daily increases exposure by {outdoor_percentage}%."
        })
        
        if outdoor_hours > 6:
            factors.append("Extended Outdoor Duration")
            
        # 3. Traffic Exposure (Distance to road)
        # ---------------------------------------------------------
        distance = data.get("distance_to_main_road", 100)
        # Closer distance = Higher risk. Normalize: 0m -> 0.2, 200m+ -> 0.0
        dist_score = max(0, (200 - distance) / 1000.0) 
        score += dist_score
        
        traffic_percentage = round(dist_score * 100, 1)
        traffic_risk = "High" if distance < 50 else "Medium" if distance < 150 else "Low"
        
        factor_details.append({
            "name": "Traffic Proximity",
            "value": f"{distance} meters",
            "contribution": traffic_percentage,
            "risk_level": traffic_risk,
            "description": f"Living {distance}m from main road contributes {traffic_percentage}% to exposure."
        })
        
        if distance < 50:
            factors.append("Proximity to Traffic")
            
        # 4. Lifestyle Factors - Smoking
        # ---------------------------------------------------------
        smoker = data.get("smoker", False)
        smoking_score = 0.15 if smoker else 0.0
        score += smoking_score
        
        smoking_percentage = round(smoking_score * 100, 1)
        
        factor_details.append({
            "name": "Smoking Status",
            "value": "Yes - Active Smoker" if smoker else "No",
            "contribution": smoking_percentage,
            "risk_level": "High" if smoker else "Low",
            "description": "Smoking significantly increases PPD absorption and health risks." if smoker 
                          else "Non-smoking status reduces additional exposure risk."
        })
        
        if smoker:
            factors.append("Smoking History")
            
        # 5. Lifestyle Factors - Two Wheeler
        # ---------------------------------------------------------
        two_wheeler = data.get("two_wheeler_use", False)
        vehicle_score = 0.1 if two_wheeler else 0.0
        score += vehicle_score
        
        vehicle_percentage = round(vehicle_score * 100, 1)
        
        factor_details.append({
            "name": "Two-Wheeler Usage",
            "value": "Regular User" if two_wheeler else "No",
            "contribution": vehicle_percentage,
            "risk_level": "Medium" if two_wheeler else "Low",
            "description": "Regular two-wheeler use increases direct exposure to traffic pollutants." if two_wheeler
                          else "No two-wheeler usage reduces direct vehicular exposure."
        })
        
        if two_wheeler:
            factors.append("Frequent Two-Wheeler Use")
            
        # Normalize score to 0.0 - 1.0 range (Clamping)
        final_score = min(max(score, 0.0), 1.0)
        
        return round(final_score, 2), {
            "key_factors": factors,
            "factor_details": factor_details,
            "total_factors_analyzed": 5
        }
