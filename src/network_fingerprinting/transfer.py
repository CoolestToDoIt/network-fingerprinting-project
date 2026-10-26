"""Validate feature provenance and evaluate historical-to-modern transfer.

A verified schema contract is mandatory. This module never converts time units,
infers session IDs, or fits preprocessing on modern data.
"""

from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd

from .data_processing import is_identifier_column, normalize_labels
from .pipeline import make_model, prediction_metrics


def validate_contract(contract: dict) -> list[str]:
    """Fail closed when extractor equivalence has not been documented."""
    if not isinstance(contract, dict):
        raise ValueError("Contract must be a JSON object.")
    if contract.get("compatibility_verified") is not True:
        raise ValueError(
            "Feature compatibility must be verified before transfer scoring."
        )
    for key in [
        "historical_extractor",
        "modern_extractor",
        "flow_settings",
        "verification_notes",
    ]:
        value = contract.get(key)
        if not value or not isinstance(value, dict):
            raise ValueError(f"Missing documented {key}.")
    for key in ["historical_extractor", "modern_extractor"]:
        if not contract[key].get("version") or not contract[key].get("source"):
            raise ValueError(f"{key} requires version and source.")
    for setting in ["timeout_seconds", "direction_rule", "active_idle_rule"]:
        if not contract["flow_settings"].get(setting):
            raise ValueError(f"Missing verified flow setting: {setting}")
    evidence = contract["verification_notes"]
    evidence_path = Path(evidence.get("fixture_report_path", ""))
    if not evidence_path.is_file() or not evidence.get("fixture_report_sha256"):
        raise ValueError(
            "A local fixture verification report and SHA-256 are required."
        )
    if (
        hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        != evidence["fixture_report_sha256"]
    ):
        raise ValueError("Fixture verification report SHA-256 mismatch.")
    definitions = contract.get("features", [])
    if not isinstance(definitions, list) or not all(
        isinstance(entry, dict) for entry in definitions
    ):
        raise ValueError("Features must be a list of definitions.")
    features = [entry.get("name") for entry in definitions]
    if (
        not features
        or any(not isinstance(name, str) or not name.strip() for name in features)
        or len(set(features)) != len(features)
    ):
        raise ValueError("Feature definitions must have unique names.")
    for entry in definitions:
        if (
            not entry.get("units")
            or not entry.get("definition")
            or is_identifier_column(entry["name"])
        ):
            raise ValueError(
                "Every feature needs units and meaning and must not be an identifier."
            )
    if contract.get("task") not in ["vpn", "tor"]:
        raise ValueError(
            "Contract task must be vpn or tor; pooled three-class data is not validated."
        )
    return features


def validate_transfer_data(
    historical: pd.DataFrame, modern: pd.DataFrame, contract: dict
):
    """Check chronology, labels, sessions, numeric schema, and direct feature overlap."""
    features = validate_contract(contract)
    frames = []
    if not historical.index.is_unique or not modern.index.is_unique:
        raise ValueError("Transfer data requires unique row indexes.")
    for name, frame in [("historical", historical), ("modern", modern)]:
        required = features + [
            "traffic_class",
            "application_category",
            "capture_year",
            "dataset_source",
        ]
        if name == "modern":
            required += ["capture_session"]
        missing = sorted(set(required) - set(frame.columns))
        if missing:
            raise ValueError(f"{name} missing required columns: {missing}")
        if frame.empty or frame[required].isna().any().any():
            raise ValueError(
                f"{name} must be nonempty with complete features and provenance."
            )
        for column in required:
            if frame[column].astype(str).str.strip().eq("").any():
                raise ValueError(f"{name} contains blank {column}.")
        numeric = frame[features].apply(pd.to_numeric, errors="raise")
        if not np.isfinite(numeric.to_numpy()).all():
            raise ValueError(
                f"{name} features must all be finite for compatibility validation."
            )
        labels = normalize_labels(frame)["label"]
        expected = {0, 1} if contract["task"] == "vpn" else {0, 2}
        if set(labels) != expected:
            raise ValueError(
                f"{name} must contain the task classes {sorted(expected)}."
            )
        if (
            frame.application_category.astype(str)
            .str.lower()
            .isin(["unknown", "nan"])
            .any()
        ):
            raise ValueError(f"{name} contains unresolved application categories.")
        frames.append((numeric, labels))
    historical_year = pd.to_numeric(historical.capture_year, errors="raise")
    modern_year = pd.to_numeric(modern.capture_year, errors="raise")
    if not (historical_year % 1 == 0).all() or not (modern_year % 1 == 0).all():
        raise ValueError("Capture years must be integers.")
    if historical_year.max() >= modern_year.min():
        raise ValueError(
            "All modern capture years must be later than all historical years."
        )
    if set(historical.dataset_source) & set(modern.dataset_source):
        raise ValueError("Historical and modern source identifiers must be disjoint.")
    if "capture_session" in historical:
        if set(historical.capture_session.dropna()) & set(modern.capture_session):
            raise ValueError("Historical and modern capture sessions overlap.")
    # Repeated feature vectors are not proof of duplicate captures, but requiring
    # review prevents silently reusing historical observations as modern traffic.
    old_hash = set(pd.util.hash_pandas_object(frames[0][0].astype(float), index=False))
    new_hash = set(pd.util.hash_pandas_object(frames[1][0].astype(float), index=False))
    if old_hash & new_hash:
        raise ValueError(
            "Exact cross-period feature overlap requires review before scoring."
        )
    for session, rows in modern.groupby("capture_session"):
        if (
            rows.traffic_class.nunique() != 1
            or rows.application_category.nunique() != 1
            or rows.capture_year.nunique() != 1
        ):
            raise ValueError(
                f"Modern session {session} has inconsistent class/category/year."
            )
    return features, frames


def run_transfer_experiment(
    historical, modern, contract, model_name="random_forest", seed=42
):
    """Train only on historical rows; test modern data, including combined shift.

    Return trained pipelines separately so the caller can store them locally.
    No synthetic validation result is presented as an observed temporal result.
    """
    features, [(old_features, old_labels), (new_features, new_labels)] = (
        validate_transfer_data(historical, modern, contract)
    )
    labels = sorted(set(old_labels))
    model = make_model(model_name, seed)
    model.fit(old_features, old_labels)
    predictions = model.predict(new_features)
    results = [
        {
            "experiment": "temporal_transfer",
            "model": model_name,
            "seed": seed,
            "n_train_samples": len(historical),
            "n_test_samples": len(modern),
            **prediction_metrics(new_labels, predictions, labels),
        }
    ]
    for category in sorted(modern.application_category.unique()):
        mask = modern.application_category == category
        results.append(
            {
                "experiment": "temporal_category",
                "held_out_category": category,
                "model": model_name,
                "seed": seed,
                "n_test_samples": int(mask.sum()),
                **prediction_metrics(new_labels[mask], predictions[mask], labels),
            }
        )
    for session, rows in modern.groupby("capture_session"):
        positions = modern.index.get_indexer(rows.index)
        results.append(
            {
                "experiment": "temporal_session",
                "capture_session": session,
                "model": model_name,
                "seed": seed,
                "n_test_samples": len(rows),
                **prediction_metrics(
                    new_labels.iloc[positions], predictions[positions], labels
                ),
            }
        )
    models = {"historical_full": model}
    for category in sorted(modern.application_category.unique()):
        train_mask = historical.application_category != category
        test_mask = modern.application_category == category
        if category not in set(historical.application_category):
            results.append(
                {
                    "experiment": "combined_shift",
                    "held_out_category": category,
                    "status": "skipped: category never present in historical dataset",
                }
            )
            continue
        if set(old_labels[train_mask]) != set(labels) or set(
            new_labels[test_mask]
        ) != set(labels):
            results.append(
                {
                    "experiment": "combined_shift",
                    "held_out_category": category,
                    "status": "skipped: missing transport class in training or category test",
                }
            )
            continue
        held_out_model = make_model(model_name, seed)
        held_out_model.fit(old_features[train_mask], old_labels[train_mask])
        result = prediction_metrics(
            new_labels[test_mask],
            held_out_model.predict(new_features[test_mask]),
            labels,
        )
        results.append(
            {
                "experiment": "combined_shift",
                "held_out_category": category,
                "model": model_name,
                "seed": seed,
                "n_train_samples": int(train_mask.sum()),
                "n_test_samples": int(test_mask.sum()),
                "train_categories": sorted(
                    historical.loc[train_mask, "application_category"].unique()
                ),
                **result,
            }
        )
        models[f"without_{category}"] = held_out_model
    return {
        "feature_columns": features,
        "results": results,
        "limitations": "Modern capture environment, protocol, and extractor differences may confound time.",
    }, models
