import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = BACKEND_DIR.parents[1] / "NLP SCAMSHIELD" / "data" / "SMSSpamCollection"
MODEL_DIR = Path(__file__).resolve().parent / "saved_models"


def train(dataset_path: Path) -> None:
    data = pd.read_csv(dataset_path, sep="\t", names=["label", "text"], encoding="utf-8")
    data = data.dropna(subset=["label", "text"])
    labels = data["label"].map({"ham": 0, "spam": 1})

    train_text, test_text, train_labels, test_labels = train_test_split(
        data["text"], labels, test_size=0.2, random_state=42, stratify=labels
    )
    vectorizer = TfidfVectorizer(
        lowercase=True,
        max_features=10000,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    train_vectors = vectorizer.fit_transform(train_text)
    test_vectors = vectorizer.transform(test_text)

    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    model.fit(train_vectors, train_labels)

    predictions = model.predict(test_vectors)
    print(f"Accuracy: {accuracy_score(test_labels, predictions):.3f}")
    print(classification_report(test_labels, predictions, target_names=["ham", "spam"]))

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_DIR / "sms_classifier.pkl")
    joblib.dump(vectorizer, MODEL_DIR / "sms_vectorizer.pkl")
    print(f"SMS model and vectorizer saved to {MODEL_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the SMS scam classifier")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    train(args.dataset)