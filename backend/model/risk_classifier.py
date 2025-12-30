def classify_risk(score):
    """
    Classifies the exposure score into risk categories.
    
    Args:
        score (float): Exposure score between 0.0 and 1.0.
        
    Returns:
        str: Risk category (LOW, MEDIUM, HIGH).
    """
    if score >= 0.7:
        return "HIGH"
    elif score >= 0.35:
        return "MEDIUM"
    else:
        return "LOW"
