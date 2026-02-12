# Google Colab Training Guide

Since no public dataset exists for "PPD Risk in Tyre Manufacturing", use this script to **generate your own dataset** and then train the model.

### Instructions
1.  Open [Google Colab](https://colab.research.google.com/).
2.  Create a **New Notebook**.
3.  Copy the code block below into a cell.
4.  Run the cell (Shift + Enter).
5.  The script will:
    *   Create a `ppd_dataset.csv` (simulating a Kaggle dataset).
    *   Train a Machine Learning Model (Random Forest).
    *   Download the trained `ppd_risk_model.pkl` file to your computer.

### Copy This Code into Colab

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib
from google.colab import files

print("Step 1: Generating Synthetic Dataset...")
# ---------------------------------------------------------
# 1. Generate Synthetic Data (Simulating a Dataset)
# ---------------------------------------------------------
np.random.seed(42)
n_samples = 2000

data = {
    'age': np.random.randint(18, 65, n_samples),
    'gender': np.random.choice(['male', 'female'], n_samples),
    'occupation': np.random.choice(
        ['tyre_worker', 'mechanic', 'painter', 'driver', 'student', 'office_worker', 'other'], 
        n_samples, 
        p=[0.3, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05]
    ),
    'outdoor_hours': np.random.randint(0, 15, n_samples),
    'distance_to_main_road': np.random.randint(5, 500, n_samples),
    'smoker': np.random.choice([True, False], n_samples, p=[0.3, 0.7]),
    'two_wheeler_use': np.random.choice([True, False], n_samples, p=[0.4, 0.6]),
    # Creatinine: random value between 0.5 and 2.0
    'creatinine': np.round(np.random.uniform(0.5, 2.0, n_samples), 2)  
}

df = pd.DataFrame(data)

# Define Logic for Target Variable (Ground Truth for Training)
# We use logic to generate the "correct answers" so the model can learn them
def calculate_risk_score(row):
    score = 0.0
    
    # Occupation Weights
    occ_weights = {'tyre_worker': 0.4, 'mechanic': 0.35, 'painter': 0.3, 'driver': 0.25}
    score += occ_weights.get(row['occupation'], 0.1)
    
    # Outdoor
    score += min(row['outdoor_hours'] / 24.0, 0.2)
    
    # Traffic
    dist_score = max(0, (200 - row['distance_to_main_road']) / 1000.0)
    score += dist_score
    
    # Lifestyle
    if row['smoker']: score += 0.15
    if row['two_wheeler_use']: score += 0.1
    
    # Random Noise (to make it realistic and not just a math equation)
    noise = np.random.normal(0, 0.02) 
    final_score = np.clip(score + noise, 0.0, 1.0)
    
    return round(final_score, 2)

df['exposure_score'] = df.apply(calculate_risk_score, axis=1)

# Save as CSV (This is your "Dataset")
df.to_csv('ppd_dataset.csv', index=False)
print("✅ Dataset 'ppd_dataset.csv' created (2000 rows).")

print("\nStep 2: Training Random Forest Model...")
# ---------------------------------------------------------
# 2. Train Model
# ---------------------------------------------------------
X = df.drop(columns=['exposure_score'])
y = df['exposure_score']

# Preprocessing Pipeline
categorical_features = ['occupation', 'gender']
numerical_features = ['age', 'outdoor_hours', 'distance_to_main_road', 'creatinine']
# Note: Boolean fields (smoker, two_wheeler) are treated as numeric/bool automatically or can be passed through

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ('bool', 'passthrough', ['smoker', 'two_wheeler_use'])
    ])

# Model Pipeline
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

# Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# Dictionary to save column names for backend verification
model_artifact = {
    'pipeline': model,
    'feature_names': list(X.columns)
}

# Save Model
joblib.dump(model, 'ppd_risk_model.pkl')
print(f"✅ Model Trained! Test R² Score: {model.score(X_test, y_test):.4f}")

print("\nStep 3: Downloading Model...")
files.download('ppd_risk_model.pkl')
```

### Next Steps
1.  Wait for the file **`ppd_risk_model.pkl`** to download.
2.  Move this file into your project folder:
    `c:\Users\Mr Sanjay Balan M\project\CCP\backend\model\`
3.  Once the file is there, restart your backend server.
