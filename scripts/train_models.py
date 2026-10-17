import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import precision_recall_curve, auc
from sklearn.ensemble import IsolationForest
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

print("Loading dataset...")
df = pd.read_csv("../data/creditcard.csv")

print("Scaling features...")
scaler = RobustScaler()
df['scaled_amount'] = scaler.fit_transform(df['Amount'].values.reshape(-1, 1))
df['scaled_time'] = scaler.fit_transform(df['Time'].values.reshape(-1, 1))
df.drop(['Time', 'Amount'], axis=1, inplace=True)

# Train-Test Split
X = df.drop('Class', axis=1)
y = df['Class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("Applying SMOTE to balance the training data for XGBoost...")
smote = SMOTE(sampling_strategy=0.1, random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

print("Training XGBoost Model (Supervised)...")
xgb_model = XGBClassifier(
    n_estimators=100, max_depth=5, learning_rate=0.1, 
    scale_pos_weight=10, random_state=42, n_jobs=-1
)
xgb_model.fit(X_train_res, y_train_res)

print("Training Isolation Forest Model (Unsupervised)...")
# Contamination is set to ~0.17% (the known fraud rate in this dataset)
iso_model = IsolationForest(
    n_estimators=100, contamination=0.0017, 
    random_state=42, n_jobs=-1
)
iso_model.fit(X_train)

print("Evaluating XGBoost model...")
y_probs = xgb_model.predict_proba(X_test)[:, 1]
precision, recall, _ = precision_recall_curve(y_test, y_probs)
pr_auc = auc(recall, precision)
print(f"\n--- XGBoost PR-AUC Score: {pr_auc:.4f} ---")

print("\nSaving model artifacts...")
os.makedirs("../models", exist_ok=True)
joblib.dump(xgb_model, "../models/aegis_xgb.pkl")
joblib.dump(iso_model, "../models/aegis_iso.pkl")  # Saving the new model
joblib.dump(scaler, "../models/aegis_scaler.pkl")
print("Saved aegis_xgb.pkl, aegis_iso.pkl, and aegis_scaler.pkl to the models directory. Training complete!")