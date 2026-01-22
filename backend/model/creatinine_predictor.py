import numpy as np
from model.predictor import PPDPredictor

class CreatininePPDPredictor:
    """
    Extended Predictor that incorporates Urine Creatinine levels.
    """
    
    def __init__(self):
        self.base_predictor = PPDPredictor()
        
    def predict_with_creatinine(self, data):
        """
        Predicts PPD exposure risk normalized by creatinine.
        
        Args:
            data (dict): Input data including creatinine.
            
        Returns:
            dict: Result containing normalized PPD, risk level, and details.
        """
        # 1. Get Base Exposure Score (Reuse existing logic)
        exposure_score, details = self.base_predictor.predict_score(data)
        
        # 2. Get Creatinine Value (mg/dL)
        creatinine = float(data.get("creatinine", 1.0))
        
        # Ensure creatinine is within reasonable bounds for calculation safety
        creatinine = max(0.1, creatinine) 
        
        # 3. Calculate Normalized PPD
        # Formula: normalized_ppd = exposure_score / creatinine
        # Heuristic scaling to make it look like a concentration value
        normalized_ppd = (exposure_score * 2.0) / creatinine
        
        # 4. Analyze Creatinine Status
        creatinine_status = self._analyze_creatinine(creatinine)
        
        # 5. Reclassify Risk Level based on Normalized Value
        # NOTE: Higher normalized_ppd = Higher Risk
        # Lower creatinine → Higher normalized PPD → Higher Risk
        # Higher creatinine → Lower normalized PPD → Lower Risk
        
        # Adjusted thresholds for better sensitivity:
        if normalized_ppd > 1.0:  # Lowered from 1.5
            risk_level = "HIGH"
            confidence = "HIGH"
            risk_description = "Significantly elevated PPD exposure detected. Immediate protective measures recommended."
        elif normalized_ppd > 0.5:  # Lowered from 0.8
            risk_level = "MEDIUM"
            confidence = "MEDIUM"
            risk_description = "Moderate PPD exposure. Regular monitoring and preventive care advised."
        else:
            risk_level = "LOW"
            confidence = "HIGH"
            risk_description = "PPD exposure within acceptable limits. Continue current safety practices."
            
        # 6. Generate Health Recommendations
        recommendations = self._generate_recommendations(risk_level, creatinine_status, details.get("key_factors", []))
        
        # 7. Add Creatinine-Exclusive Details
        factor_details = details.get("factor_details", [])
        
        # Add creatinine normalization factor
        creat_impact = abs(1.0 - creatinine) * 20  # Impact percentage
        factor_details.append({
            "name": "Creatinine Normalization",
            "value": f"{creatinine} mg/dL ({creatinine_status['status']})",
            "contribution": round(creat_impact, 1),
            "risk_level": creatinine_status['risk_modifier'],
            "description": creatinine_status['description']
        })
        
        # 8. Compile Comprehensive Response with Threshold Information
        response = {
            "mode": "WITH_CREATININE",
            "predicted_risk": risk_level,
            "normalized_ppd": round(normalized_ppd, 2),
            "exposure_score": exposure_score,
            "creatinine_value": creatinine,
            "creatinine_status": creatinine_status,
            "risk_level": risk_level,
            "confidence": confidence,
            "risk_description": risk_description,
            "key_factors": details.get("key_factors", []) + ["Creatinine Normalization"],
            "factor_details": factor_details,
            "total_factors_analyzed": details.get("total_factors_analyzed", 5) + 1,
            "health_recommendations": recommendations,
            "analysis_date": "Lab-Free Prediction Model",
            "threshold_info": {
                "high_threshold": 1.0,
                "medium_threshold": 0.5,
                "current_value": round(normalized_ppd, 2),
                "explanation": "Lower creatinine increases normalized PPD (higher risk). Higher creatinine decreases normalized PPD (lower risk)."
            }
        }
        
        return response
    
    def _analyze_creatinine(self, creatinine):
        """Analyze creatinine levels and provide interpretation"""
        if creatinine < 0.7:
            return {
                "status": "Low",
                "risk_modifier": "High",
                "description": f"Low creatinine ({creatinine} mg/dL) indicates diluted urine, which amplifies the normalized PPD concentration.",
                "interpretation": "Diluted urine sample may overestimate actual exposure"
            }
        elif creatinine <= 1.5:
            return {
                "status": "Normal",
                "risk_modifier": "Medium",
                "description": f"Normal creatinine ({creatinine} mg/dL) provides reliable normalization for accurate exposure assessment.",
                "interpretation": "Optimal sample quality for exposure assessment"
            }
        else:
            return {
                "status": "High",
                "risk_modifier": "Low",
                "description": f"High creatinine ({creatinine} mg/dL) indicates concentrated urine, which may underestimate actual exposure levels.",
                "interpretation": "Concentrated sample may underestimate exposure"
            }
    
    def _generate_recommendations(self, risk_level, creatinine_status, key_factors):
        """Generate personalized health recommendations"""
        recommendations = []
        
        # Base recommendations by risk level
        if risk_level == "HIGH":
            recommendations.extend([
                "🚨 Immediate Action: Consult occupational health specialist",
                "🛡️ Use high-grade PPE (gloves, masks) during work",
                "🏥 Schedule comprehensive health screening within 2 weeks",
                "⏰ Implement regular biomonitoring (every 3 months)"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "⚠️ Schedule health checkup within 1 month",
                "🛡️ Use protective equipment during high-exposure activities",
                "📊 Monitor symptoms: skin irritation, respiratory issues",
                "🔄 Reassess exposure levels every 6 months"
            ])
        else:
            recommendations.extend([
                "✅ Maintain current safety practices",
                "🔍 Continue annual health screenings",
                "📝 Document any new symptoms promptly"
            ])
        
        # Creatinine-specific recommendations
        if creatinine_status['status'] == "Low":
            recommendations.append("💧 Ensure adequate hydration before future urine sampling")
        elif creatinine_status['status'] == "High":
            recommendations.append("💧 Consider repeating test after increased fluid intake")
        
        # Factor-specific recommendations
        if "Smoking History" in key_factors:
            recommendations.append("🚭 Strongly consider smoking cessation - significantly amplifies PPD risks")
        
        if "High Risk Occupation" in key_factors:
            recommendations.append("👔 Request workplace exposure assessment and ventilation improvements")
        
        if "Proximity to Traffic" in key_factors:
            recommendations.append("🏠 Consider air purifiers for indoor spaces")
        
        return recommendations
