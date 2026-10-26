"""Export historical tables plus a readable data-quality and provenance report."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from network_fingerprinting.data_loaders import (
    load_application_vpn_dataset,
    load_tor_dataset,
)
from network_fingerprinting.pipeline import _prepare_model_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("data/processed/historical")
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {}
    sources = {
        "vpn": Path("data/raw/Scenario B-ARFF.zip"),
        "tor": Path("data/raw/Scenario-A-merged_5s.csv"),
    }
    for task, path in sources.items():
        frame = (
            load_application_vpn_dataset(path, 15).drop_duplicates()
            if task == "vpn"
            else load_tor_dataset(path)
        ).reset_index(drop=True)
        features, labels = _prepare_model_data(frame)
        canonical = features.copy()
        canonical["traffic_class"] = labels.map({0: "normal", 1: "vpn", 2: "tor"})
        if "application_category" in frame:
            canonical["application_category"] = frame.application_category
        canonical["dataset_source"] = f"ISCX2016_{task}"
        # Dataset-level provenance, not a fabricated per-flow timestamp.
        canonical["capture_year"] = 2016
        canonical.to_csv(args.output / f"{task}.csv", index=False)
        report[task] = {
            "input_path": str(path),
            "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "n_rows": len(frame),
            "feature_columns": features.columns.tolist(),
            "class_counts": {str(k): int(v) for k, v in labels.value_counts().items()},
            "missing_numeric_cells": int(features.isna().sum().sum()),
            "duplicate_feature_vectors": int(features.duplicated().sum()),
            "feature_vectors_with_conflicting_labels": int(
                pd.DataFrame(
                    {
                        "feature_hash": pd.util.hash_pandas_object(
                            features, index=False
                        ),
                        "label": labels,
                    }
                )
                .groupby("feature_hash")
                .label.nunique()
                .gt(1)
                .sum()
            ),
            "historical_capture_sessions_available": False,
            "capture_year_basis": "Dataset identity ISCX2016; individual timestamps unavailable.",
            "application_categories_available": "application_category" in frame,
            "transfer_compatibility_verified": False,
            "all_missing_features": features.columns[features.isna().all()].tolist(),
        }
    (args.output / "quality_report.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    target = Path("reports/completion_study")
    target.mkdir(parents=True, exist_ok=True)
    (target / "dataset_quality.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
