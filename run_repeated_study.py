"""Five-seed, two-model VPN study; fixed LOAO tests and stratified training bootstrap."""

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

from network_fingerprinting.data_loaders import load_application_vpn_dataset
from network_fingerprinting.pipeline import run_baseline_experiment, run_loao_experiment

METRICS = ["accuracy", "macro_f1", "macro_precision", "macro_recall"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/vpn_study"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    raw = load_application_vpn_dataset(args.dataset, 15)
    df = raw.drop_duplicates().reset_index(drop=True)
    results = []
    seeds = [42, 43, 44, 45, 46]
    for model in ["logistic_regression", "random_forest"]:
        for seed in seeds:
            baseline = run_baseline_experiment(df, model, seed)
            baseline["held_out_category"] = "baseline"
            results.append(baseline)
            for category in sorted(df.application_category.unique()):
                results.append(run_loao_experiment(df, category, model, seed, True))
            print(f"Completed {model}, seed {seed}", flush=True)
    # Full-training LOAO controls separate held-out-category effects from bootstrap effects.
    reference = [
        run_loao_experiment(df, category, model, 42, False)
        for model in ["logistic_regression", "random_forest"]
        for category in sorted(df.application_category.unique())
    ]
    (args.output / "full_training_reference.json").write_text(
        json.dumps(
            [
                {k: v for k, v in r.items() if k not in {"predictions", "true_labels"}}
                for r in reference
            ],
            indent=2,
        )
    )
    metadata = {
        "sha256": hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
        "timeout_seconds": 15,
        "raw_rows": len(raw),
        "deduplicated_rows": len(df),
        "duplicates_removed": len(raw) - len(df),
        "seeds": seeds,
        "python": platform.python_version(),
        "sklearn": sklearn.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "loao_variation": "training bootstrap within category and class; fixed test flows",
        "baseline_variation": "stratified 75/25 split seed and estimator seed",
        "random_forest": {"n_estimators": 200, "min_samples_leaf": 2},
        "session_disjoint": "unavailable: no real session metadata",
    }
    # Keep large predictions outside the repository; compact results are report artifacts.
    detail = Path("data/processed/vpn_study")
    detail.mkdir(parents=True, exist_ok=True)
    (detail / "predictions.json").write_text(json.dumps(results, indent=2))
    compact = [
        {k: v for k, v in r.items() if k not in {"predictions", "true_labels"}}
        for r in results
    ]
    (args.output / "metrics.json").write_text(
        json.dumps({"metadata": metadata, "results": compact}, indent=2)
    )
    runs = pd.DataFrame(compact)
    runs[["model", "seed", "experiment", "held_out_category"] + METRICS].to_csv(
        args.output / "runs.csv", index=False
    )
    summary = runs.groupby(["model", "held_out_category"])[METRICS].agg(["mean", "std"])
    summary.columns = ["_".join(c) for c in summary.columns]
    summary.reset_index().to_csv(args.output / "summary.csv", index=False)
    print(summary.to_string(), flush=True)


if __name__ == "__main__":
    main()
