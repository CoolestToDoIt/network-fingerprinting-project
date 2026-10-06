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
            df[col] = df[col].map(
                lambda x: x.decode("utf-8") if isinstance(x, (bytes, bytearray)) else x
            )

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
        raise ValueError(
            "The dataset does not contain a class column for VPN vs Non-VPN classification."
        )

    df["traffic_class"] = df[class_col].astype(str).str.strip().str.lower()
    df["label"] = df["traffic_class"].map(
        {"non-vpn": 0, "non_vpn": 0, "nonvpn": 0, "vpn": 1, "openvpn": 1}
    )

    if df["label"].isna().any():
        unknown = sorted(
            df.loc[df["label"].isna(), class_col].astype(str).unique().tolist()
        )
        raise ValueError(f"Unexpected class values in VPN dataset: {unknown}")

    return df


def load_application_vpn_dataset(path: str | Path, timeout: int = 15) -> pd.DataFrame:
    """Load one Scenario B variant; AllinOne variants lose the VPN label."""
    member_suffix = f"TimeBasedFeatures-Dataset-{timeout}s.arff"
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if n.endswith("/" + member_suffix)]
        if len(members) != 1:
            raise ValueError(
                f"Expected exactly one {member_suffix}; found {len(members)}."
            )
        df = _read_arff_from_bytes(archive.read(members[0]))
    labels = df["class1"].str.strip().str.upper()
    categories = labels.str.removeprefix("VPN-")
    mapping = {
        "BROWSING": "browsing",
        "CHAT": "chat",
        "MAIL": "email",
        "FT": "file_transfer",
        "P2P": "p2p",
        "STREAMING": "streaming",
        "VOIP": "voip",
    }
    if not categories.isin(mapping).all():
        raise ValueError("Unexpected application labels in Scenario B.")
    df["application_category"] = categories.map(mapping)
    df["traffic_class"] = labels.str.startswith("VPN-").map(
        {True: "vpn", False: "non-vpn"}
    )
    df["dataset_source"] = members[0]
    return df


def load_tor_dataset(path: str | Path) -> pd.DataFrame:
    """Load binary Scenario A CSV, excluding endpoint identifiers and exact duplicates.

    Scenario B contains application labels only and is intentionally rejected.
    Units and timeout remain source-defined; this is not a VPN feature adapter.
    """
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names after trimming whitespace.")
    if "label" not in df:
        raise ValueError("Tor CSV must contain a label column.")
    labels = df["label"].astype(str).str.strip().str.lower()
    if not labels.isin(["tor", "nontor"]).all():
        raise ValueError(
            "Expected TOR/nonTOR binary labels; application-only Scenario B is not a binary dataset."
        )
    # Deduplicate before removing endpoints so distinct flows are not collapsed.
    df = df.drop_duplicates().copy()
    df["traffic_class"] = (
        df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"tor": "tor", "nontor": "non_tor"})
    )
    df = df.drop(
        columns=[
            "Source IP",
            "Destination IP",
            "Source Port",
            "Destination Port",
            "label",
        ],
        errors="ignore",
    )
    df["dataset_source"] = Path(path).name
    return df
