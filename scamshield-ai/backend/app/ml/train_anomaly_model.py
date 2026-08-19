import sys
sys.path.append(".")

import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
from pathlib import Path

from app.database import SessionLocal
from app.db_models import ScanRecord

db = SessionLocal()
records = db.query(ScanRecord).filter(ScanRecord.input_type == "url").all()
db.close()

print(f"Found {len(records)} URL scan records")

if len(records) < 20:
    print("WARNING: Very few records available. Isolation Forest works best with more data.")
    print("Run a few more /analyze scans on different domains first, then re-run this script.")

# Build a feature table from stored factors + trust_score
rows = []
for r in records:
    factors_by_name = {f["name"]: f for f in (r.factors or [])}

    def status_score(name):
        f = factors_by_name.get(name)
        if not f:
            return 50  # neutral if missing
        return {"good": 100, "warning": 50, "bad": 0}.get(f["status"], 50)

    rows.append({
        "trust_score": r.trust_score,
        "domain_age_score": status_score("Domain Age"),
        "safe_browsing_score": status_score("Google Safe Browsing"),
        "virustotal_score": status_score("VirusTotal"),
        "community_score": status_score("Community Reports"),
    })

df = pd.DataFrame(rows)
print(f"\nTraining data shape: {df.shape}")
print(df.describe())

model = IsolationForest(
    n_estimators=100,
    contamination=0.1,   # assume ~10% of scans are anomalous — tune as data grows
    random_state=42,
)
model.fit(df)

model_dir = Path(__file__).parent / "saved_models"
model_dir.mkdir(exist_ok=True)
joblib.dump(model, model_dir / "anomaly_detector.pkl")
joblib.dump(list(df.columns), model_dir / "anomaly_feature_columns.pkl")
print(f"\nAnomaly model saved to {model_dir / 'anomaly_detector.pkl'}")