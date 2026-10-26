"""Save full-historical-data models and human-readable model cards locally."""

import hashlib
import json
import platform
from pathlib import Path

import joblib
import sklearn

from network_fingerprinting.data_loaders import (
    load_application_vpn_dataset,
    load_tor_dataset,
)
from network_fingerprinting.pipeline import _prepare_model_data, make_model


def main():
    output = Path("models/historical")
    output.mkdir(parents=True, exist_ok=True)
    cards = Path("reports/model_cards")
    cards.mkdir(parents=True, exist_ok=True)
    sources = {
        "vpn": Path("data/raw/Scenario B-ARFF.zip"),
        "tor": Path("data/raw/Scenario-A-merged_5s.csv"),
    }
    for task, path in sources.items():
        frame = (
            load_application_vpn_dataset(path).drop_duplicates()
            if task == "vpn"
            else load_tor_dataset(path)
        )
        features, labels = _prepare_model_data(frame)
        for model_name in ["logistic_regression", "random_forest"]:
            model = make_model(model_name, 42)
            model.fit(features, labels)
            name = f"{task}_{model_name}"
            artifact = output / f"{name}.joblib"
            joblib.dump(model, artifact)
            metadata = {
                "task": task,
                "model": model_name,
                "seed": 42,
                "n_training_flows": len(frame),
                "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "model_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "feature_columns": features.columns.tolist(),
                "class_labels": (
                    {"0": "Non-VPN", "1": "VPN"}
                    if task == "vpn"
                    else {"0": "NonTor", "2": "Tor"}
                ),
                "python": platform.python_version(),
                "scikit_learn": sklearn.__version__,
                "intended_use": "Research inference within the same verified historical schema.",
                "modern_feature_compatibility_verified": False,
                "limitations": [
                    "Not a three-class classifier.",
                    "No independent temporal or session validation.",
                    "Full-data fitting is for a frozen inference artifact, not evaluation.",
                    "Do not load untrusted joblib files.",
                ],
            }
            (output / f"{name}.json").write_text(json.dumps(metadata, indent=2) + "\n")
            (cards / f"{name}.json").write_text(json.dumps(metadata, indent=2) + "\n")
            print(f"Saved {artifact}", flush=True)


if __name__ == "__main__":
    main()
