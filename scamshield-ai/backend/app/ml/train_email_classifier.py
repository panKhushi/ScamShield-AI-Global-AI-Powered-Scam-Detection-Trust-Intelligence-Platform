import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib
from pathlib import Path

df = pd.read_csv("app/ml/data/phising_email1.csv")
df = df.dropna(subset=["text_combined"])

X_text = df["text_combined"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X_text, y, test_size=0.2, random_state=42, stratify=y
)

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english",
    ngram_range=(1, 2),
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42,
)
model.fit(X_train_vec, y_train)

y_pred = model.predict(X_test_vec)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print(classification_report(y_test, y_pred, target_names=["legit", "phishing"]))

model_dir = Path(__file__).parent / "saved_models"
model_dir.mkdir(exist_ok=True)
joblib.dump(model, model_dir / "email_classifier.pkl")
joblib.dump(vectorizer, model_dir / "email_vectorizer.pkl")
print(f"\nModel + vectorizer saved to {model_dir}")