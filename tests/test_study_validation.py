"""Scientific split invariants and failure modes for stricter experiments."""

import numpy as np
import pandas as pd
import pytest

from network_fingerprinting.features import build_flow_features
from network_fingerprinting.pipeline import (
    _prepare_model_data,
    _evaluate,
    prediction_metrics,
)
from network_fingerprinting.study import (
    feature_groups,
    grouped_baseline,
    matched_category_experiment,
)
from test_loao_pipeline import dataset


def test_matched_test_rows_training_sizes_and_category_membership():
    frame = dataset()
    # Avoid the synthetic fixture's repeated feature vectors across all categories.
    frame["duration"] = np.arange(len(frame), dtype=float)
    seen, unseen = matched_category_experiment(frame, "chat", "logistic_regression", 42)
    assert seen["test_fingerprint"] == unseen["test_fingerprint"]
    assert seen["true_labels"] == unseen["true_labels"]
    assert seen["n_train_samples"] == unseen["n_train_samples"]
    assert "chat" in seen["train_categories"]
    assert "chat" not in unseen["train_categories"]
    assert seen["feature_group_overlap"] == unseen["feature_group_overlap"] == 0


def test_grouped_split_never_shares_exact_features_even_when_labels_conflict():
    frame = dataset()
    frame["duration"] = np.tile(np.arange(12), 6)
    groups = feature_groups(frame)
    assert groups.nunique() == 12
    result = grouped_baseline(frame, "logistic_regression", 42)
    assert result["feature_group_overlap"] == 0
    assert result["n_train_samples"] + result["n_test_samples"] == len(frame)


@pytest.mark.parametrize(
    "column",
    [
        "Source Port",
        " Destination Port",
        "capture_id",
        "pair_id",
        "sample_id",
        "capture_year",
        "Flow ID",
    ],
)
def test_numeric_identifiers_are_never_features(column):
    frame = dataset()
    frame[column] = np.arange(len(frame))
    features, _ = _prepare_model_data(frame)
    assert column not in features


def test_feature_schema_mismatch_is_explained():
    frame = dataset()
    with pytest.raises(ValueError, match="match exactly"):
        _evaluate(frame, frame.assign(unexpected_feature=1))


def test_fake_counts_are_rejected_and_zero_duration_is_missing():
    with pytest.raises(ValueError, match="genuine"):
        build_flow_features(
            pd.DataFrame(
                {
                    "duration": [10],
                    "total_fiat": [3],
                    "total_biat": [4],
                    "flowBytesPerSecond": [100],
                }
            )
        )
    frame = pd.DataFrame(
        {
            "flow_duration": [0.0, 2.0],
            "total_fwd_packets": [1, 3],
            "total_bwd_packets": [1, 1],
            "total_fwd_bytes": [10, 30],
            "total_bwd_bytes": [5, 10],
        }
    )
    features = build_flow_features(frame)
    assert pd.isna(features.bytes_per_second.iloc[0])
    assert features.bytes_per_second.iloc[1] == 20
    assert features.packets_per_second.iloc[1] == 2


def test_per_class_metrics_retain_absent_test_class():
    result = prediction_metrics([0, 0], [0, 1], [0, 1])
    assert result["per_class"]["0"]["recall"] == 0.5
    assert result["per_class"]["1"]["support"] == 0
    assert result["confusion_matrix"] == [[1, 1], [0, 0]]
