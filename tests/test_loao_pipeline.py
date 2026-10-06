import pandas as pd
import pytest

from network_fingerprinting.pipeline import (
    _prepare_model_data,
    run_loao_experiment,
    run_session_disjoint_experiment,
)


def dataset():
    return pd.DataFrame(
        [
            {
                "duration": i + label * 10,
                "traffic_class": "vpn" if label else "non-vpn",
                "application_category": category,
                "capture_session": f"{category}-{i}",
                "label": label,
                "class1": label,
                "session_id": i,
                "capture_year": 2016,
            }
            for category in ["chat", "email", "voip"]
            for label in [0, 1]
            for i in range(12)
        ]
    )


def test_loao_excludes_entire_category_and_reports_confusion_matrix():
    result = run_loao_experiment(dataset(), "chat")
    assert result["train_categories"] == ["email", "voip"]
    assert result["n_train_samples"] == 48
    assert result["n_test_samples"] == 24
    assert sum(map(sum, result["confusion_matrix"])) == 24
    assert result["test_class_counts"] == {"0": 12, "1": 12}


def test_targets_and_numeric_metadata_cannot_be_features():
    X, _ = _prepare_model_data(dataset())
    assert X.columns.tolist() == ["duration"]


def test_session_split_rejects_missing_or_null_metadata():
    with pytest.raises(ValueError, match="Real, non-null"):
        run_session_disjoint_experiment(dataset().drop(columns="capture_session"))
    df = dataset()
    df.loc[0, "capture_session"] = None
    with pytest.raises(ValueError, match="Real, non-null"):
        run_session_disjoint_experiment(df)


def test_loao_rejects_single_class_test():
    df = dataset()
    df = df[~((df.application_category == "chat") & (df.traffic_class == "vpn"))]
    with pytest.raises(ValueError, match="both VPN and Non-VPN"):
        run_loao_experiment(df, "chat")
