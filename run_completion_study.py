"""Run and checkpoint stricter historical experiments without modern-data claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

from network_fingerprinting.data_loaders import (
    load_application_vpn_dataset,
    load_tor_dataset,
)
from network_fingerprinting.pipeline import run_baseline_experiment, run_loao_experiment
from network_fingerprinting.study import grouped_baseline, matched_category_experiment


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/final_study.json"))
    parser.add_argument(
        "--vpn", type=Path, default=Path("data/raw/Scenario B-ARFF.zip")
    )
    parser.add_argument(
        "--tor", type=Path, default=Path("data/raw/Scenario-A-merged_5s.csv")
    )
    parser.add_argument("--output", type=Path, default=Path("reports/completion_study"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if (
        config["random_forest_trees"] != 200
        or config["random_forest_min_samples_leaf"] != 2
    ):
        raise ValueError(
            "Model factory currently supports the recorded 200-tree, leaf-size-2 setup only."
        )
    vpn_raw = load_application_vpn_dataset(args.vpn, config["vpn_timeout_seconds"])
    vpn = vpn_raw.drop_duplicates().reset_index(drop=True)
    tor = load_tor_dataset(args.tor).reset_index(drop=True)
    metadata = {
        "config": config,
        "config_sha256": digest(args.config),
        "input_sha256": {"vpn": digest(args.vpn), "tor": digest(args.tor)},
        "source_sha256": {
            str(p): digest(p)
            for p in [
                Path(__file__),
                *sorted(Path("src/network_fingerprinting").glob("*.py")),
            ]
        },
        "environment": {
            "python": platform.python_version(),
            "sklearn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "vpn_raw_rows": len(vpn_raw),
        "vpn_unique_rows": len(vpn),
        "tor_unique_rows": len(tor),
        "session_status": "No genuine historical session identifiers available.",
        "temporal_status": "No modern traffic available; no real temporal result.",
    }
    run_signature = hashlib.sha256(
        json.dumps(metadata, sort_keys=True).encode()
    ).hexdigest()
    checkpoint = Path("data/processed/completion_study") / run_signature[:16]
    checkpoint.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    all_results = []

    def run(name, function):
        path = checkpoint / f"{name}.json"
        if path.exists():
            results = json.loads(path.read_text())
        else:
            results = function()
            results = results if isinstance(results, list) else [results]
            path.write_text(json.dumps(results, indent=2) + "\n")
        for result in results:
            result["run_id"] = name
        all_results.extend(results)
        print(f"Completed {name}", flush=True)

    categories = sorted(vpn.application_category.unique())
    for model in config["models"]:
        for seed in config["seeds"]:
            run(
                f"vpn_grouped_{model}_{seed}",
                lambda: grouped_baseline(vpn, model, seed, config["test_fraction"]),
            )
            run(
                f"tor_random_{model}_{seed}",
                lambda: run_baseline_experiment(tor, model, seed),
            )
            run(
                f"tor_grouped_{model}_{seed}",
                lambda: grouped_baseline(tor, model, seed, config["test_fraction"]),
            )
            for category in categories:
                run(
                    f"vpn_matched_{category}_{model}_{seed}",
                    lambda: matched_category_experiment(
                        vpn, category, model, seed, config["test_fraction"]
                    ),
                )
        # One full-training duration ablation; fixed partition, diagnostic only.
        for feature_set, frame in [
            ("native", vpn),
            ("without_duration", vpn.drop(columns="duration")),
        ]:
            for category in categories:
                run(
                    f"vpn_{feature_set}_{category}_{model}_42",
                    lambda: {
                        **run_loao_experiment(frame, category, model, 42),
                        "feature_set": feature_set,
                    },
                )
    compact = [
        {
            key: value
            for key, value in result.items()
            if key not in {"predictions", "true_labels"}
        }
        for result in all_results
    ]
    (args.output / "metrics.json").write_text(
        json.dumps(
            {"run_signature": run_signature, "metadata": metadata, "results": compact},
            indent=2,
        )
        + "\n"
    )
    columns = [
        "run_id",
        "model",
        "seed",
        "experiment",
        "condition",
        "held_out_category",
        "feature_set",
        "accuracy",
        "macro_f1",
        "macro_precision",
        "macro_recall",
        "n_train_samples",
        "n_test_samples",
    ]
    pd.DataFrame(compact).reindex(columns=columns).to_csv(
        args.output / "runs.csv", index=False
    )
    print(
        f"Saved {len(compact)} evaluations to {args.output}; predictions in {checkpoint}",
        flush=True,
    )


if __name__ == "__main__":
    main()
