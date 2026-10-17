
# 🛡️ AegisPay AI

> **Pluggable Real-Time Fraud & Anomaly Detection Microservice API (INR / ₹)**

AegisPay AI is an ultra-low latency, pluggable microservice engineered to evaluate financial transaction risk in real time before payment authorization. Positioned as an asynchronous middleware layer between payment gateways (e.g., Stripe, Razorpay), banking infrastructures, and e-commerce platforms, AegisPay AI ingests multi-dimensional transaction payloads, runs anomaly detection algorithms, and returns actionable risk verdicts in under 20 milliseconds.

---

## 🚀 Key Features

* **Universal Pluggable Architecture:** Exposes REST (`POST /v1/evaluate-transaction`) and WebSocket (`/ws/stream`) interfaces for payment gateways and risk teams.
* **4-Tier Defense Engine:**
  1. **Deterministic Hard Rules:** Instantly blocks transactions exceeding ₹50,000,000 (50 Lakhs) or originating from blacklisted IPs.
  2. **Feature Engineering:** Computes Z-scores and channel-specific risk signals (Bank Transfers, Debit, Credit).
  3. **Supervised ML (XGBoost):** Evaluates complex fraud patterns (PR-AUC: 0.8278).
  4. **Unsupervised Anomaly Detection (Isolation Forest):** Flags novel, out-of-distribution spending anomalies.
* **Low-Latency Performance:** Sub-30ms execution speed per transaction.
* **Live Cybertech Dashboard:** Single-page dark/cyan monitoring dashboard built with WebSockets streaming live evaluations at 60 FPS.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, WebSockets
* **Machine Learning:** XGBoost, Scikit-Learn (Isolation Forest), Imbalanced-Learn (SMOTE)
* **Frontend:** HTML5, CSS3 (Cybertech Dark Theme), Vanilla JavaScript (WebSockets)
* **Data Processing:** Pandas, NumPy, Joblib

---

## 📦 Project Structure

```text
Agespay ai/
├── data/                  # Kaggle dataset directory (git-ignored)
├── models/                # Serialized XGBoost & Isolation Forest artifacts
├── scripts/
│   └── train_models.py    # Model training pipeline
├── src/
│   ├── main.py            # FastAPI server & WebSocket routes
│   ├── ml_engine.py       # 4-Tier decision engine
│   ├── feature_engineering.py  # Statistical feature extractor
│   └── schemas.py         # Pydantic JSON request/response contracts
├── static/
│   ├── index.html         # Live Risk Dashboard UI
│   ├── style.css          # Cybertech dark mode styling
│   └── app.js             # Client WebSocket handler
├── requirements.txt
└── README.md
```
