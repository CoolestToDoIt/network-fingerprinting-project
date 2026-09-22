from __future__ import annotations

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from .data_processing import normalize_labels
from .features import build_flow_features


def _prepare_model_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    processed = normalize_labels(df.copy())
    processed = build_flow_features(processed)

    feature_columns = [
        c
        for c in processed.columns
        if c not in {"traffic_class", "application_category", "capture_session", "dataset_source", "capture_year"}
        and pd.api.types.is_numeric_dtype(processed[c])
    ]

    X = processed[feature_columns]
    y = processed["label"]
    return X, y


def run_baseline_experiment(df: pd.DataFrame) -> dict:
    """Run a simple baseline model to verify the preprocessing pipeline."""
    X, y = _prepare_model_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "macro_f1": f1_score(y_test, predictions, average="macro"),
        "macro_precision": precision_score(y_test, predictions, average="macro", zero_division=0),
        "macro_recall": recall_score(y_test, predictions, average="macro", zero_division=0),
        "n_test_samples": len(y_test),
        "predictions": predictions.tolist(),
        "true_labels": y_test.tolist(),
    }
    return metrics


def run_session_disjoint_experiment(df: pd.DataFrame, test_fraction: float = 0.25) -> dict:
    """Split by capture session so flows from the same session cannot appear in both train and test."""
    if "capture_session" not in df.columns:
        df = df.copy()
        df["capture_session"] = [f"session_{idx}" for idx in range(len(df))]

    sessions = sorted(df["capture_session"].unique().tolist())
    if len(sessions) < 2:
        raise ValueError("At least two capture sessions are required to run a session-disjoint split.")

    test_count = max(1, int(round(len(sessions) * test_fraction)))
    test_sessions = sessions[:test_count]
    train_sessions = [s for s in sessions if s not in test_sessions]

    train_df = df[df["capture_session"].isin(train_sessions)].copy()
    test_df = df[df["capture_session"].isin(test_sessions)].copy()

    X_train, y_train = _prepare_model_data(train_df)
    X_test, y_test = _prepare_model_data(test_df)

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "macro_f1": f1_score(y_test, predictions, average="macro"),
        "macro_precision": precision_score(y_test, predictions, average="macro", zero_division=0),
        "macro_recall": recall_score(y_test, predictions, average="macro", zero_division=0),
        "n_test_samples": len(y_test),
        "predictions": predictions.tolist(),
        "true_labels": y_test.tolist(),
        "train_sessions": train_sessions,
        "test_sessions": test_sessions,
    }
    return metrics
