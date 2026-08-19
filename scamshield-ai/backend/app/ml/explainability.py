import shap
import pandas as pd
from app.ml.predictor import load_model, build_feature_vector

_explainer = None


def _get_explainer():
    """Lazily creates a SHAP TreeExplainer for the trained RandomForest model."""
    global _explainer
    if _explainer is None:
        model, _ = load_model()
        _explainer = shap.TreeExplainer(model)
    return _explainer

def explain_prediction(computed_features: dict, top_n: int = 5) -> list[dict]:
    """
    Returns the top N features that most influenced this specific prediction,
    with their SHAP contribution value (positive = pushed toward "scam",
    negative = pushed toward "legitimate").
    """
    explainer = _get_explainer()
    X = build_feature_vector(computed_features)

    shap_values = explainer.shap_values(X)

    # Handle different SHAP output shapes across versions:
    # - list of 2 arrays (older versions): [class_0_values, class_1_values]
    # - 3D array (newer versions): shape (samples, features, classes)
    # - 2D array (some binary setups): shape (samples, features)
    if isinstance(shap_values, list):
        contributions = shap_values[1][0]
    else:
        arr = shap_values
        if arr.ndim == 3:
            contributions = arr[0, :, 1]   # sample 0, all features, class 1
        else:
            contributions = arr[0]

    contributions = [float(v) for v in contributions]

    feature_names = X.columns.tolist()
    pairs = list(zip(feature_names, contributions))

    pairs.sort(key=lambda p: abs(p[1]), reverse=True)
    top_pairs = pairs[:top_n]

    explanation = []
    for name, value in top_pairs:
        explanation.append({
            "feature": name,
            "contribution": round(value, 3),
            "direction": "increases_risk" if value > 0 else "decreases_risk",
        })

    return explanation