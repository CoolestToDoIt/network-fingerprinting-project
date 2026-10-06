"""Train classifiers and evaluate random, session, and application-category splits.

Metadata and target columns are excluded from the numeric feature matrix.
All learned preprocessing is fitted only on the experiment's training rows.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from .data_processing import LEAKAGE_COLUMNS, normalize_labels

METADATA = {
    "traffic_class",
    "application_category",
    "application",
    "capture_session",
    "dataset_source",
    "capture_year",
    "class",
    "class1",
}


def _prepare_model_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    # Preserve labels separately; never allow them or grouping metadata into X.
    processed = normalize_labels(df.copy())
    columns = [
        c
        for c in processed
        if c not in LEAKAGE_COLUMNS | METADATA
        and pd.api.types.is_numeric_dtype(processed[c])
    ]
    if not columns:
        raise ValueError("No numeric flow features available.")
    return processed[columns].replace([np.inf, -np.inf], np.nan), processed["label"]


def _evaluate(
    train: pd.DataFrame,
    test: pd.DataFrame,
    model_name: str = "logistic_regression",
    seed: int = 42,
    bootstrap_training: bool = False,
) -> dict:
    # Resample only training rows, retaining each category/class stratum size.
    if bootstrap_training:
        grouping = ["traffic_class"]
        if "application_category" in train:
            grouping.append("application_category")
        train = train.groupby(grouping, group_keys=False, sort=True).sample(
            frac=1, replace=True, random_state=seed
        )
    if model_name not in {"logistic_regression", "random_forest"}:
        raise ValueError(f"Unknown model: {model_name}")
    X_train, y_train = _prepare_model_data(train)
    X_test, y_test = _prepare_model_data(test)
    if y_train.nunique() < 2:
        raise ValueError("Training split must contain at least two classes.")
    if set(y_test) - set(y_train):
        raise ValueError("Test split contains classes absent from training.")
    model = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scaler", StandardScaler()),
            (
                "classifier",
                (
                    LogisticRegression(max_iter=3000, random_state=seed)
                    if model_name == "logistic_regression"
                    else RandomForestClassifier(
                        n_estimators=200,
                        min_samples_leaf=2,
                        random_state=seed,
                        n_jobs=-1,
                    )
                ),
            ),
        ]
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test[X_train.columns])
    labels = sorted(set(y_train) | set(y_test))
    return {
        "model": model_name,
        "seed": seed,
        "bootstrap_training": bootstrap_training,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "macro_f1": float(
            f1_score(
                y_test, predictions, labels=labels, average="macro", zero_division=0
            )
        ),
        "macro_precision": float(
            precision_score(
                y_test, predictions, labels=labels, average="macro", zero_division=0
            )
        ),
        "macro_recall": float(
            recall_score(
                y_test, predictions, labels=labels, average="macro", zero_division=0
            )
        ),
        "confusion_matrix": confusion_matrix(
            y_test, predictions, labels=labels
        ).tolist(),
        "confusion_matrix_labels": labels,
        "n_train_samples": len(train),
        "n_test_samples": len(test),
        "feature_columns": X_train.columns.tolist(),
        "train_class_counts": {
            str(k): int(v) for k, v in y_train.value_counts().items()
        },
        "test_class_counts": {str(k): int(v) for k, v in y_test.value_counts().items()},
        "predictions": predictions.tolist(),
        "true_labels": y_test.tolist(),
    }


def run_baseline_experiment(
    df: pd.DataFrame, model_name: str = "logistic_regression", seed: int = 42
) -> dict:
    _, y = _prepare_model_data(df)
    train, test = train_test_split(df, test_size=0.25, random_state=seed, stratify=y)
    return {"experiment": "baseline", **_evaluate(train, test, model_name, seed)}


def run_session_disjoint_experiment(
    df: pd.DataFrame, test_fraction: float = 0.25
) -> dict:
    if "capture_session" not in df or df["capture_session"].isna().any():
        raise ValueError(
            "Real, non-null capture_session IDs are required; row IDs are not sessions."
        )
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between zero and one.")
    if df["capture_session"].nunique() < 2:
        raise ValueError("At least two capture sessions are required.")
    _, y = _prepare_model_data(df)
    splitter = GroupShuffleSplit(n_splits=100, test_size=test_fraction, random_state=42)
    for train_idx, test_idx in splitter.split(df, y, groups=df["capture_session"]):
        if set(y.iloc[train_idx]) == set(y) == set(y.iloc[test_idx]):
            train, test = df.iloc[train_idx], df.iloc[test_idx]
            return {
                "experiment": "session_disjoint",
                **_evaluate(train, test),
                "train_sessions": sorted(train["capture_session"].unique().tolist()),
                "test_sessions": sorted(test["capture_session"].unique().tolist()),
            }
    raise ValueError(
        "No session-disjoint split with all classes in both partitions found in 100 attempts."
    )


def run_loao_experiment(
    df: pd.DataFrame,
    held_out_category: str,
    model_name: str = "logistic_regression",
    seed: int = 42,
    bootstrap_training: bool = False,
) -> dict:
    if "application_category" not in df or df["application_category"].isna().any():
        raise ValueError("Non-null application_category metadata is required.")
    categories = df["application_category"].astype(str).str.strip().str.lower()
    held_out_category = held_out_category.strip().lower()
    if held_out_category == "unknown" or (categories == "unknown").any():
        raise ValueError("Unknown application categories must be resolved before LOAO.")
    test_mask = categories == held_out_category
    if not test_mask.any() or test_mask.all():
        raise ValueError(
            "LOAO requires a present held-out category and other training categories."
        )
    train, test = df.loc[~test_mask], df.loc[test_mask]
    if normalize_labels(test)["label"].nunique() < 2:
        raise ValueError("Held-out category must contain both VPN and Non-VPN traffic.")
    return {
        "experiment": "loao",
        "held_out_category": held_out_category,
        "train_categories": sorted(categories[~test_mask].unique().tolist()),
        **_evaluate(train, test, model_name, seed, bootstrap_training),
    }
