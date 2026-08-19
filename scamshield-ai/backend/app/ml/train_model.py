import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
from pathlib import Path

df = pd.read_csv("app/ml/data/phishing.csv")

# Drop the Index column — not a real feature
df = df.drop(columns=["Index"])

FEATURE_COLUMNS = [c for c in df.columns if c != "class"]

X = df[FEATURE_COLUMNS]
y = df["class"].map({1: 0, -1: 1})  # relabel: 0 = legit, 1 = phishing (scam)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    random_state=42,
    class_weight="balanced",
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print(classification_report(y_test, y_pred, target_names=["legit", "phishing"]))

model_dir = Path(__file__).parent / "saved_models"
model_dir.mkdir(exist_ok=True)
joblib.dump(model, model_dir / "scam_classifier.pkl")
joblib.dump(FEATURE_COLUMNS, model_dir / "feature_columns.pkl")  # save exact column order
print(f"\nModel saved to {model_dir / 'scam_classifier.pkl'}")

importances = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS).sort_values(ascending=False)
print("\nTop 10 most important features:")
print(importances.head(10))