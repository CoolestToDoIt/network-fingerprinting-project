"""Score real modern CSVs only after a feature-provenance contract passes validation."""

import argparse
import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd

from network_fingerprinting.transfer import run_transfer_experiment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("historical_csv", type=Path)
    parser.add_argument("modern_csv", type=Path)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument(
        "--model",
        choices=["logistic_regression", "random_forest"],
        default="random_forest",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/processed/transfer"))
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    historical, modern = pd.read_csv(args.historical_csv), pd.read_csv(args.modern_csv)
    report, models = run_transfer_experiment(
        historical, modern, contract, args.model, args.seed
    )
    report["sha256"] = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [args.historical_csv, args.modern_csv, args.contract]
    }
    report["contract"] = contract
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    joblib.dump(
        {
            "models": models,
            "feature_columns": report["feature_columns"],
            "contract": contract,
        },
        args.output / "historical_models.joblib",
    )
    print(f"Saved historical-only models and modern scores to {args.output}")


if __name__ == "__main__":
    main()
