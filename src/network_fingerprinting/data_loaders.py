from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
from scipy.io import arff


def _read_arff_from_bytes(raw_bytes: bytes) -> pd.DataFrame:
    """Read a single ARFF file into a DataFrame while preserving nominal label values."""
    text = raw_bytes.decode("utf-8", errors="replace")
    data, _ = arff.loadarff(io.StringIO(text))
    df = pd.DataFrame(data)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(lambda x: x.decode("utf-8") if isinstance(x, (bytes, bytearray)) else x)

    return df


def load_vpn_dataset(path: str | Path) -> pd.DataFrame:
    """Load the current VPN/non-VPN ARFF-based dataset from the local raw folder."""
    dataset_path = Path(path)
    if dataset_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(dataset_path, "r") as archive:
            members = [m for m in archive.namelist() if m.lower().endswith(".arff")]
            if not members:
                raise ValueError(f"No .arff files found in archive: {dataset_path}")
            with archive.open(members[0]) as fh:
                df = _read_arff_from_bytes(fh.read())
    elif dataset_path.suffix.lower() == ".arff":
        df = _read_arff_from_bytes(dataset_path.read_bytes())
    else:
        raise ValueError(f"Unsupported dataset format: {dataset_path}")

    class_col = None
    for candidate in ["class1", "class", "label", "traffic_class"]:
        if candidate in df.columns:
            class_col = candidate
            break

    if class_col is None:
        raise ValueError("The dataset does not contain a class column for VPN vs Non-VPN classification.")

    df["traffic_class"] = df[class_col].astype(str).str.strip().str.lower()
    df["label"] = df["traffic_class"].map({"non-vpn": 0, "non_vpn": 0, "nonvpn": 0, "vpn": 1, "openvpn": 1})

    if df["label"].isna().any():
        unknown = sorted(df.loc[df["label"].isna(), class_col].astype(str).unique().tolist())
        raise ValueError(f"Unexpected class values in VPN dataset: {unknown}")

    return df
