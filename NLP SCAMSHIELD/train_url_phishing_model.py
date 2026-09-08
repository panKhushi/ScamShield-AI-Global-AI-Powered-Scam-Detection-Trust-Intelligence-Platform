"""Train and save the URL-only phishing detection pipeline."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from url_feature_extractor import URL_FEATURE_COLUMNS


ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models"
TARGET_COLUMN = "Result"
RANDOM_STATE = 42


def find_phishing_dataset() -> Path:
    required_columns = set(URL_FEATURE_COLUMNS) | {TARGET_COLUMN}
    candidates = []
    for path in (ROOT / "data").glob("*.csv"):
        columns = set(pd.read_csv(path, nrows=0).columns)
        if required_columns.issubset(columns):
            candidates.append(path)
    if len(candidates) != 1:
        raise ValueError(
            f"Expected exactly one phishing CSV with the required columns; found {candidates}"
        )
    return candidates[0]


def train_and_save() -> dict:
    data_path = find_phishing_dataset()
    dataframe = pd.read_csv(data_path)
    required_columns = set(URL_FEATURE_COLUMNS) | {TARGET_COLUMN}
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing_columns)}")

    clean_data = dataframe.replace([float("inf"), float("-inf")], pd.NA).dropna()
    clean_data = clean_data.drop_duplicates().reset_index(drop=True)
    clean_data = clean_data.loc[:, URL_FEATURE_COLUMNS + [TARGET_COLUMN]]
    features = clean_data[URL_FEATURE_COLUMNS]
    target = clean_data[TARGET_COLUMN].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=target,
    )

    model_factories = {
        "Logistic Regression": lambda: LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "Random Forest": lambda: RandomForestClassifier(
            n_estimators=300,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            class_weight="balanced",
        ),
        "SVM": lambda: SVC(probability=True, random_state=RANDOM_STATE, class_weight="balanced"),
    }
    results = {}
    fitted_models = {}

    for name, factory in model_factories.items():
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", factory()),
        ])
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        results[name] = {
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions, pos_label=-1),
            "recall": recall_score(y_test, predictions, pos_label=-1),
            "f1_score": f1_score(y_test, predictions, pos_label=-1),
        }
        fitted_models[name] = pipeline
        print(f"\n{name}")
        print(classification_report(y_test, predictions, labels=[-1, 1], target_names=["Phishing", "Legitimate"], zero_division=0))

    # F1 is the selection metric for the phishing class (-1); recall breaks ties.
    best_name = max(
        results,
        key=lambda name: (results[name]["f1_score"], results[name]["recall"], results[name]["precision"]),
    )
    best_pipeline = fitted_models[best_name]
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(best_pipeline, MODEL_DIR / "url_phishing_pipeline.pkl")
    joblib.dump(best_pipeline, MODEL_DIR / "url_phishing_model.pkl")
    joblib.dump(
        {
            "feature_columns": URL_FEATURE_COLUMNS,
            "target_column": TARGET_COLUMN,
            "label_mapping": {-1: "Phishing / Suspicious", 1: "Legitimate / Safe"},
            "selected_model": best_name,
            "metrics": results,
            "source_dataset": str(data_path.name),
            "deduplicated_rows": len(clean_data),
        },
        MODEL_DIR / "url_phishing_metadata.pkl",
    )
    print(f"Selected model: {best_name}")
    print(pd.DataFrame(results).T.round(4).to_string())
    return {"selected_model": best_name, "metrics": results}


if __name__ == "__main__":
    train_and_save()
