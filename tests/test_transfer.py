"""Synthetic fixtures validate transfer machinery; they are not temporal results."""

import copy
import hashlib

import pandas as pd
import pytest

from network_fingerprinting.transfer import (
    run_transfer_experiment,
    validate_transfer_data,
)


@pytest.fixture
def transfer_fixture(tmp_path):
    evidence = tmp_path / "synthetic_fixture_report.txt"
    evidence.write_text("Synthetic test only: feature is a unitless artificial number.")
    contract = {
        "compatibility_verified": True,
        "task": "vpn",
        "historical_extractor": {"version": "synthetic", "source": "test"},
        "modern_extractor": {"version": "synthetic", "source": "test"},
        "flow_settings": {
            "timeout_seconds": 15,
            "direction_rule": "synthetic",
            "active_idle_rule": "synthetic",
        },
        "verification_notes": {
            "fixture_report_path": str(evidence),
            "fixture_report_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
        },
        "features": [
            {"name": "duration", "units": "synthetic", "definition": "Test value only"}
        ],
    }
    historical = pd.DataFrame(
        [
            {
                "duration": category_index * 100 + sample + label * 10,
                "traffic_class": "vpn" if label else "normal",
                "application_category": category,
                "capture_year": 2016,
                "dataset_source": "synthetic_old",
            }
            for category_index, category in enumerate(["chat", "browsing"])
            for label in [0, 1]
            for sample in range(8)
        ]
    )
    modern = pd.DataFrame(
        [
            {
                "duration": 1000 + category_index * 100 + label * 10 + sample,
                "traffic_class": "vpn" if label else "normal",
                "application_category": category,
                "capture_year": 2026,
                "dataset_source": "synthetic_new",
                "capture_session": f"new_{category}_{label}",
            }
            for category_index, category in enumerate(["chat", "browsing"])
            for label in [0, 1]
            for sample in range(3)
        ]
    )
    return historical, modern, contract


def test_transfer_preprocessing_is_fitted_only_on_history(transfer_fixture):
    old, new, contract = transfer_fixture
    report, models = run_transfer_experiment(old, new, contract, "logistic_regression")
    assert (
        models["historical_full"].named_steps["scaler"].mean_[0] == old.duration.mean()
    )
    assert len(report["results"][0]["predictions"]) == len(new)
    combined = [
        result
        for result in report["results"]
        if result["experiment"] == "combined_shift"
    ]
    assert len(combined) == 2
    for result in combined:
        assert result["held_out_category"] not in result["train_categories"]
        assert result["n_test_samples"] == 6
    assert (
        len(
            [
                result
                for result in report["results"]
                if result["experiment"] == "temporal_session"
            ]
        )
        == 4
    )


@pytest.mark.parametrize(
    "change, message",
    [
        ("pending", "verified"),
        ("year", "later"),
        ("source", "disjoint"),
        ("overlap", "overlap"),
        ("session", "consistent"),
        ("missing", "missing required"),
        ("infinite", "finite"),
        ("evidence", "SHA-256"),
        ("target_feature", "identifier"),
    ],
)
def test_invalid_transfer_data_fails_closed(transfer_fixture, change, message):
    old, new, contract = transfer_fixture
    contract = copy.deepcopy(contract)
    if change == "pending":
        contract["compatibility_verified"] = False
    if change == "year":
        new["capture_year"] = 2016
    if change == "source":
        new["dataset_source"] = "synthetic_old"
    if change == "overlap":
        new.loc[0, "duration"] = old.loc[0, "duration"]
    if change == "session":
        new.loc[0, "application_category"] = "different"
    if change == "missing":
        new = new.drop(columns="capture_session")
    if change == "infinite":
        new["duration"] = new["duration"].astype(float)
        new.loc[0, "duration"] = float("inf")
    if change == "evidence":
        contract["verification_notes"]["fixture_report_sha256"] = "wrong"
    if change == "target_feature":
        contract["features"] = [
            {"name": "capture_year", "units": "year", "definition": "metadata"}
        ]
    with pytest.raises(ValueError, match=message):
        validate_transfer_data(old, new, contract)


def test_transfer_cli_saves_historical_only_artifacts(transfer_fixture, tmp_path):
    import json
    import subprocess
    import sys
    import joblib

    old, new, contract = transfer_fixture
    old_path = tmp_path / "historical.csv"
    new_path = tmp_path / "modern.csv"
    contract_path = tmp_path / "contract.json"
    output = tmp_path / "synthetic_output"
    old.to_csv(old_path, index=False)
    new.to_csv(new_path, index=False)
    contract_path.write_text(json.dumps(contract))
    subprocess.run(
        [
            sys.executable,
            "run_transfer.py",
            str(old_path),
            str(new_path),
            "--contract",
            str(contract_path),
            "--model",
            "logistic_regression",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads((output / "metrics.json").read_text())
    assert len(report["sha256"]) == 3
    artifacts = joblib.load(output / "historical_models.joblib")
    assert (
        artifacts["models"]["historical_full"].named_steps["scaler"].mean_[0]
        == old.duration.mean()
    )
    assert artifacts["feature_columns"] == ["duration"]
