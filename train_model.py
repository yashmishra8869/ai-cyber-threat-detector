from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import CONFUSION_MATRIX_PATH, DATASET_PATH, METRICS_PATH, MODEL_PATH
from schema import (
    CATEGORICAL_FEATURES,
    EXPECTED_COLUMNS,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    convert_target_to_binary,
    validate_categorical_values,
    validate_expected_schema,
    validate_numeric_values,
)


FEATURES_FOR_MODEL = [column for column in FEATURE_COLUMNS if column not in [TARGET_COLUMN]]


def ensure_dataset_exists(dataset_path: str | Path = DATASET_PATH) -> Path:
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(
            "NSL-KDD training dataset not found. Download the genuine 'KDDTrain+.txt' file from the official NSL-KDD dataset source, "
            "and place it at: " + str(path) + ". The file must contain the 41 traffic features plus 'attack_name' and 'difficulty'."
        )
    return path


def load_nsl_kdd_dataset(dataset_path: str | Path = DATASET_PATH) -> pd.DataFrame:
    path = ensure_dataset_exists(dataset_path)
    df = pd.read_csv(path, header=None, names=EXPECTED_COLUMNS, na_values='?')
    validate_expected_schema(df)
    validate_numeric_values(df, NUMERIC_FEATURES)
    validate_categorical_values(df, CATEGORICAL_FEATURES)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Dataset is missing the target column '{TARGET_COLUMN}'.")

    df["target_binary"] = convert_target_to_binary(df[TARGET_COLUMN])
    return df


def build_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])
    categorical_transformer = Pipeline(steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))])

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", model)])


def train_pipeline_from_dataframe(df: pd.DataFrame) -> tuple[Pipeline, dict]:
    if TARGET_COLUMN in df.columns and "target_binary" not in df.columns:
        df = df.copy()
        df["target_binary"] = convert_target_to_binary(df[TARGET_COLUMN])
    elif "target_binary" not in df.columns:
        raise ValueError("The dataset must contain a binary target column named 'target_binary' or the original 'attack_name' column.")

    X = df[FEATURE_COLUMNS]
    y = df["target_binary"]

    validate_expected_schema(df)
    validate_numeric_values(df, NUMERIC_FEATURES)
    validate_categorical_values(df, CATEGORICAL_FEATURES)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 6),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 6),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 6),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 6),
        "classification_report": classification_report(y_test, y_pred, zero_division=0, output_dict=True),
    }

    labels = [0, 1]
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    metrics["confusion_matrix"] = cm.tolist()

    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation="nearest", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.colorbar()
    plt.xticks([0, 1], ["Normal", "Attack"])
    plt.yticks([0, 1], ["Normal", "Attack"])
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH)
    plt.close()

    return pipeline, metrics


def save_pipeline_and_metrics(pipeline: Pipeline, metrics: dict, model_path: str | Path = MODEL_PATH, metrics_path: str | Path = METRICS_PATH) -> None:
    model_path = Path(model_path)
    metrics_path = Path(metrics_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def train_model() -> dict:
    df = load_nsl_kdd_dataset(DATASET_PATH)
    pipeline, metrics = train_pipeline_from_dataframe(df)
    save_pipeline_and_metrics(pipeline, metrics, MODEL_PATH, METRICS_PATH)
    return metrics


if __name__ == "__main__":
    try:
        metrics = train_model()
        print("Training completed successfully.")
        print(json.dumps(metrics, indent=2))
    except FileNotFoundError as exc:
        print(f"Dataset error: {exc}")
        raise SystemExit(1)
    except ValueError as exc:
        print(f"Validation error: {exc}")
        raise SystemExit(1)
