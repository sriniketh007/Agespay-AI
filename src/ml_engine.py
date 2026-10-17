import joblib
import numpy as np
import hashlib
import os

# Get the absolute path to the models directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XGB_PATH = os.path.join(BASE_DIR, 'models', 'aegis_xgb.pkl')
ISO_PATH = os.path.join(BASE_DIR, 'models', 'aegis_iso.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'aegis_scaler.pkl')

print("Loading ML models into memory...")
xgb_model = joblib.load(XGB_PATH)
iso_model = joblib.load(ISO_PATH)
scaler = joblib.load(SCALER_PATH)

# Production Rule Configs
MAX_SINGLE_TRANSACTION_LIMIT = 5000000.00  # $50,000 Hard Ceiling
BLACKLISTED_IPS = {"192.168.1.255", "10.0.0.99", "185.220.101.5"}

# Baseline statistical constants from Kaggle dataset
DATASET_MEAN_AMOUNT = 2500.00
DATASET_STD_AMOUNT = 7500.00

def generate_mock_pca_features(account_id: str, device_ip: str):
    """Simulates the V1-V28 hidden features by hashing the account and IP."""
    seed = int(hashlib.sha256(f"{account_id}{device_ip}".encode()).hexdigest(), 16) % (10**8)
    np.random.seed(seed)
    return np.random.randn(28)

def evaluate_transaction(amount: float, account_id: str, device_ip: str):
    reasons = []

    # =========================================================
    # TIER 1: DETERMINISTIC HARD RULES (Runs BEFORE ML Models)
    # =========================================================
    if amount >= MAX_SINGLE_TRANSACTION_LIMIT:
        reasons.append("EXCEEDS_HARD_TRANSACTION_CEILING")
        return 0.9999, "DECLINED_FRAUD", reasons

    if device_ip in BLACKLISTED_IPS:
        reasons.append("KNOWN_MALICIOUS_IP_ADDRESS")
        return 0.9800, "DECLINED_FRAUD", reasons

    if amount <= 0:
        reasons.append("INVALID_TRANSACTION_AMOUNT")
        return 0.9900, "DECLINED_FRAUD", reasons

    # =========================================================
    # TIER 2: FEATURE SCALING & STATISTICAL CHECKS
    # =========================================================
    scaled_amount = scaler.transform([[amount]])[0][0]
    scaled_time = scaler.transform([[0]])[0][0] 
    
    # Calculate Statistical Z-Score
    amount_z_score = (amount - DATASET_MEAN_AMOUNT) / DATASET_STD_AMOUNT

    # Generate feature array for XGBoost & Isolation Forest
    pca_features = generate_mock_pca_features(account_id, device_ip)
    final_features = np.concatenate([pca_features, [scaled_amount, scaled_time]])
    feature_array = [final_features]
    
    # =========================================================
    # TIER 3: SUPERVISED ML + UNSUPERVISED ANOMALY DETECTION
    # =========================================================
    xgb_risk_score = float(xgb_model.predict_proba(feature_array)[0][1])
    
    iso_prediction = iso_model.predict(feature_array)[0]
    is_anomaly = (iso_prediction == -1)
    
    final_risk_score = xgb_risk_score

    # Statistical Outlier Bump
    if amount_z_score > 3.0:
        reasons.append(f"HIGH_STATISTICAL_OUTLIER_ZSCORE_{round(amount_z_score, 1)}")
        final_risk_score = max(final_risk_score, 0.65)  # Force at least Medium Risk

    # Anomaly Model Bump
    if is_anomaly:
        reasons.append("UNSUPERVISED_ANOMALY_DETECTED")
        final_risk_score += 0.20
        final_risk_score = min(final_risk_score, 0.99)
            
    # =========================================================
    # TIER 4: BUSINESS DECISION TRIAGE
    # =========================================================
    if final_risk_score > 0.85:
        verdict = "DECLINED_FRAUD"
        if not reasons:
            reasons.extend(["HIGH_RISK_SIGNATURE", "VELOCITY_ANOMALY"])
    elif final_risk_score >= 0.60:
        verdict = "CHALLENGE_PUSH"
        if not reasons:
            reasons.extend(["UNUSUAL_AMOUNT_PATTERN"])
    else:
        verdict = "APPROVED"
        
    return round(final_risk_score, 4), verdict, reasons