import zipfile
from pathlib import Path

import pandas as pd

from network_fingerprinting.data_loaders import load_vpn_dataset


def test_load_vpn_dataset_loads_arff_zip_and_maps_binary_class(tmp_path: Path):
    arff_text = """@RELATION test-vpn

@ATTRIBUTE duration NUMERIC
@ATTRIBUTE total_fiat NUMERIC
@ATTRIBUTE total_biat NUMERIC
@ATTRIBUTE class1 {Non-VPN,VPN}

@DATA
1,10,5,Non-VPN
2,20,6,VPN
3,30,7,Non-VPN
"""

    zip_path = tmp_path / "sample.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("sample.arff", arff_text)

    df = load_vpn_dataset(zip_path)

    assert list(df.columns)[:3] == ["duration", "total_fiat", "total_biat"]
    assert set(df["label"].unique()) == {0, 1}
    assert df["traffic_class"].tolist() == ["non-vpn", "vpn", "non-vpn"]
    assert df["label"].tolist() == [0, 1, 0]
