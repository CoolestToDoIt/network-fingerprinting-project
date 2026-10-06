import pandas as pd
import pytest

from network_fingerprinting.data_loaders import load_tor_dataset
from network_fingerprinting.pipeline import _prepare_model_data


def test_tor_loader_removes_identifiers_duplicates_and_target(tmp_path):
    p = tmp_path / "tor.csv"
    rows = [
        {
            " Source Port": 443,
            "Source IP": "10.0.0.1",
            " Flow Duration": 7,
            "label": "TOR",
        },
        {
            " Source Port": 80,
            "Source IP": "10.0.0.2",
            " Flow Duration": 9,
            "label": "nonTOR",
        },
    ]
    pd.DataFrame(rows + rows[:1]).to_csv(p, index=False)
    d = load_tor_dataset(p)
    X, y = _prepare_model_data(d)
    assert len(d) == 2
    assert X.columns.tolist() == ["Flow Duration"]
    assert y.tolist() == [2, 0]


def test_application_only_csv_is_rejected(tmp_path):
    p = tmp_path / "categories.csv"
    pd.DataFrame({"label": ["CHAT", "VOIP"]}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="application-only"):
        load_tor_dataset(p)
