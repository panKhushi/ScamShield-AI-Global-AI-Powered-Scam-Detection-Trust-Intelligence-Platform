import joblib
from pathlib import Path
import pandas as pd

MODEL_DIR = Path(__file__).parent / "saved_models"

_anomaly_model = None
_anomaly_columns = None


def _load_anomaly_model():
    global _anomaly_model, _anomaly_columns
    if _anomaly_model is None:
        _anomaly_model = joblib.load(MODEL_DIR / "anomaly_detector.pkl")
        _anomaly_columns = joblib.load(MODEL_DIR / "anomaly_feature_columns.pkl")
    return _anomaly_model, _anomaly_columns


def detect_anomaly(trust_score: int, factors: list) -> dict:
    """
    Runs the trained Isolation Forest against this scan's derived features.
    Returns a dict with is_anomaly (bool) and anomaly_score (float,
    lower = more anomalous, per sklearn's convention).
    """
    model, columns = _load_anomaly_model()

    factors_by_name = {f.name: f for f in factors}

    def status_score(name):
        f = factors_by_name.get(name)
        if not f:
            return 50
        return {"good": 100, "warning": 50, "bad": 0}.get(f.status, 50)

    row = {
        "trust_score": trust_score,
        "domain_age_score": status_score("Domain Age"),
        "safe_browsing_score": status_score("Google Safe Browsing"),
        "virustotal_score": status_score("VirusTotal"),
        "community_score": status_score("Community Reports"),
    }

    X = pd.DataFrame([row], columns=columns)

    prediction = model.predict(X)[0]   # 1 = normal, -1 = anomaly
    score = model.decision_function(X)[0]   # lower = more anomalous

    return {
        "is_anomaly": bool(prediction == -1),
        "anomaly_score": round(float(score), 3),
    }