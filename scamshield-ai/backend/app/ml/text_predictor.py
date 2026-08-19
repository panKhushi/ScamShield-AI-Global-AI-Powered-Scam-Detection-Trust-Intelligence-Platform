import joblib
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "saved_models"

_job_model = None
_job_vectorizer = None
_email_model = None
_email_vectorizer = None


def _load_job_model():
    global _job_model, _job_vectorizer
    if _job_model is None:
        _job_model = joblib.load(MODEL_DIR / "job_classifier.pkl")
        _job_vectorizer = joblib.load(MODEL_DIR / "job_vectorizer.pkl")
    return _job_model, _job_vectorizer


def _load_email_model():
    global _email_model, _email_vectorizer
    if _email_model is None:
        _email_model = joblib.load(MODEL_DIR / "email_classifier.pkl")
        _email_vectorizer = joblib.load(MODEL_DIR / "email_vectorizer.pkl")
    return _email_model, _email_vectorizer


def predict_job_scam_probability(text: str) -> float:
    model, vectorizer = _load_job_model()
    X = vectorizer.transform([text])
    proba = model.predict_proba(X)[0]  # [prob_legit, prob_fraudulent]
    return round(float(proba[1]) * 100, 1)


def predict_email_phishing_probability(text: str) -> float:
    model, vectorizer = _load_email_model()
    X = vectorizer.transform([text])
    proba = model.predict_proba(X)[0]  # [prob_legit, prob_phishing]
    return round(float(proba[1]) * 100, 1)