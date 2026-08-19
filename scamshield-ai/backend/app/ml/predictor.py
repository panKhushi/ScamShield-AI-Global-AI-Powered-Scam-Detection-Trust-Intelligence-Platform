import joblib
from pathlib import Path
import pandas as pd

MODEL_DIR = Path(__file__).parent / "saved_models"

_model = None
_feature_columns = None

def load_model():
    global _model, _feature_columns
    if _model is None:
        _model = joblib.load(MODEL_DIR / "scam_classifier.pkl")
        _feature_columns = joblib.load(MODEL_DIR / "feature_columns.pkl")
    return _model, _feature_columns


def build_feature_vector(computed: dict) -> pd.DataFrame:
    """
    Builds the full 31-column feature vector the model expects.
    Any feature not in `computed` (i.e. not scraped/calculated) defaults to 0 (neutral/unknown).
    """
    _, feature_columns = load_model()

    row = {col: computed.get(col, 0) for col in feature_columns}
    return pd.DataFrame([row], columns=feature_columns)


def predict_scam_probability(computed: dict) -> float:
    """
    Returns probability (0-100) that the site is a scam/phishing site.
    """
    model, _ = load_model()
    X = build_feature_vector(computed)
    proba = model.predict_proba(X)[0]  # [prob_legit, prob_phishing] since class 1 = phishing
    return round(float(proba[1]) * 100, 1)