"""Run reproducible baseline and category-held-out VPN experiments."""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from network_fingerprinting.data_loaders import load_application_vpn_dataset
from network_fingerprinting.pipeline import (
    run_baseline_experiment,
    run_loao_experiment,
    run_session_disjoint_experiment,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--timeout", type=int, default=15, choices=[15, 30, 60, 120])
    parser.add_argument(
        "--output", type=Path, default=Path("data/processed/generalization")
    )
    args = parser.parse_args()
    df = load_application_vpn_dataset(args.dataset, args.timeout)
    args.output.mkdir(parents=True, exist_ok=True)
    results = [run_baseline_experiment(df)]
    for category in sorted(df.application_category.unique()):
        results.append(run_loao_experiment(df, category))
    try:
        results.append(run_session_disjoint_experiment(df))
        session_status = "completed"
    except ValueError as error:
        session_status = str(error)
    report = {
        "dataset_sha256": hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
        "timeout_seconds": args.timeout,
        "n_samples": len(df),
        "seed": 42,
        "session_disjoint_status": session_status,
        "results": results,
    }
    (args.output / "metrics.json").write_text(json.dumps(report, indent=2))
    columns = [
        "experiment",
        "held_out_category",
        "accuracy",
        "macro_f1",
        "macro_precision",
        "macro_recall",
        "n_train_samples",
        "n_test_samples",
    ]
    summary = pd.DataFrame(results).reindex(columns=columns)
    summary.to_csv(args.output / "comparison.csv", index=False)
    print(summary.to_string(index=False))
    print("Session-disjoint:", session_status)


if __name__ == "__main__":
    main()
