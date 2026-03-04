import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

def generate_synthetic_data(n_samples=5000):
    np.random.seed(42)
    
    # --- Demographic Features ---
    ages = np.random.randint(18, 70, n_samples)
    genders = np.random.choice(['Male', 'Female', 'Other'], n_samples)
    occupations = np.random.choice(
        ['Student', 'Tyre Worker', 'Mechanic', 'Painter', 'Driver', 'Office Worker', 'Other', 'Doctor', 'Farmer', 'Teacher'], 
        n_samples
    )
    outdoor_hours = np.random.randint(0, 14, n_samples)
    distances = np.random.randint(0, 500, n_samples)
    smokers = np.random.choice([0, 1], n_samples, p=[0.7, 0.3]) # 0=No, 1=Yes
    two_wheeler = np.random.choice([0, 1], n_samples)

    # --- New Medical History Features ---
    # More likely to have symptoms if smoker or high risk occupation
    respiratory_symptoms = np.zeros(n_samples)
    skin_allergy_history = np.zeros(n_samples)
    
    for i in range(n_samples):
        base_prob = 0.1
        if smokers[i]: base_prob += 0.2
        if occupations[i] in ['Tyre Worker', 'Mechanic', 'Painter']: base_prob += 0.2
        respiratory_symptoms[i] = np.random.choice([0, 1], p=[1-base_prob, base_prob])
        
        allergy_prob = 0.1
        if occupations[i] in ['Painter', 'Tyre Worker']: allergy_prob += 0.2
        skin_allergy_history[i] = np.random.choice([0, 1], p=[1-allergy_prob, allergy_prob])

    # --- New Clinical/Lab Features ---
    # Generate realistic distributions based on user rules
    # IgE: Normal 0-100, Mod 101-300, High >300
    ige_levels = np.random.lognormal(mean=4.0, sigma=1.0, size=n_samples) # skewed distribution
    
    # Eosinophil: Normal 1-4, Mod 5-7, High >7
    eosinophil_pct = np.random.normal(loc=3, scale=2, size=n_samples)
    eosinophil_pct = np.clip(eosinophil_pct, 0, 20)

    # FEV1: Normal >=80, Mod 60-79, High <60
    fev1_predicted = np.random.normal(loc=90, scale=15, size=n_samples)
    fev1_predicted = np.clip(fev1_predicted, 20, 120)

    # Patch Test: 0=Neg, 1=Weak, 2=Strong
    patch_test = np.random.choice([0, 1, 2], n_samples, p=[0.8, 0.15, 0.05])

    # --- Risk Labeling Logic (The Ground Truth) ---
    risk_labels = []

    for i in range(n_samples):
        # 1. User's Clinical Rules (Overrides others)
        clinical_high = (
            (patch_test[i] == 2) or 
            (ige_levels[i] > 300 and eosinophil_pct[i] > 7) or 
            (fev1_predicted[i] < 60)
        )
        
        clinical_moderate = (
            (ige_levels[i] >= 101 and ige_levels[i] <= 300) or
            (eosinophil_pct[i] >= 5 and eosinophil_pct[i] <= 7) or
            (fev1_predicted[i] >= 60 and fev1_predicted[i] <= 79) or
            (patch_test[i] == 1)
        )

        # 2. Occupational/Demographic Logic (Base Risk)
        occ_high = occupations[i] in ['Tyre Worker', 'Mechanic', 'Painter']
        occ_mod = occupations[i] in ['Driver', 'Traffic Police', 'Farmer']
        
        lifestyle_risk = (smokers[i] + (outdoor_hours[i] > 6)) >= 2
        history_risk = (respiratory_symptoms[i] + skin_allergy_history[i]) >= 1

        # Final Decision
        if clinical_high:
            risk = 'High'
        elif clinical_moderate:
            if occ_high or lifestyle_risk:
                risk = 'High' # Escalates moderate clinical if Occ is also high
            else:
                risk = 'Medium'
        elif occ_high or lifestyle_risk or history_risk:
            risk = 'Medium' # Base logical risk
            if occ_high and history_risk:
                risk = 'High'
        else:
            risk = 'Low'
            
        risk_labels.append(risk)

    # Create DataFrame
    df = pd.DataFrame({
        'Age': ages,
        'Gender': genders,
        'Occupation': occupations,
        'Outdoor_Hours': outdoor_hours,
        'Distance_to_Road': distances,
        'Smoker': smokers,
        'Two_Wheeler': two_wheeler,
        'Respiratory_Symptoms': respiratory_symptoms,
        'Skin_Allergy_History': skin_allergy_history,
        'IgE_Level': ige_levels,
        'Eosinophil_Percentage': eosinophil_pct,
        'FEV1': fev1_predicted,
        'Patch_Test': patch_test,
        'Risk_Label': risk_labels
    })

    return df

def train_new_model():
    print("Generating synthetic data...")
    df = generate_synthetic_data(6000)
    
    # Preprocessing
    # Encode Categorical
    le_gender = LabelEncoder()
    df['Gender'] = le_gender.fit_transform(df['Gender'])
    
    le_occ = LabelEncoder()
    df['Occupation'] = le_occ.fit_transform(df['Occupation'])

    X = df.drop('Risk_Label', axis=1)
    y = df['Risk_Label']

    # Train Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model
    print("Training Random Forest...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    # Save Artifacts
    print("Saving model and encoders...")
    joblib.dump(clf, 'ppd_risk_model_v2.pkl')
    joblib.dump(le_gender, 'encoder_gender_v2.pkl')
    joblib.dump(le_occ, 'encoder_occupation_v2.pkl')
    
    print("Done!")

if __name__ == "__main__":
    train_new_model()
