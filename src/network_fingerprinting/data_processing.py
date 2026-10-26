from __future__ import annotations

from typing import Iterable

import pandas as pd

LEAKAGE_COLUMNS = {
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "source_ip",
    "destination_ip",
    "ip_address",
    "host",
    "hostname",
    "domain",
    "sni",
    "tls_sni",
    "filename",
    "capture_name",
    "session_id",
    "application_name",
    "label",
}


METADATA_COLUMNS = {
    "traffic_class",
    "application_category",
    "application",
    "capture_session",
    "dataset_source",
    "capture_year",
    "capture_id",
    "sample_id",
    "pair_id",
    "time_period",
    "collection_day",
    "class",
    "class1",
    "label",
    "timestamp",
    "start_utc",
    "end_utc",
    "session_id",
    "dataset",
    "flow_id",
    "protocol_label",
}


def is_identifier_column(column: str) -> bool:
    """Recognize common endpoint, target and provenance fields despite CSV spelling."""
    import re

    name = re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower()).strip("_")
    return name in LEAKAGE_COLUMNS | METADATA_COLUMNS | {
        "destination_port",
        "source_port",
        "source_mac",
        "destination_mac",
        "src_mac",
        "dst_mac",
        "ip",
        "mac",
        "capture_file",
        "file_name",
    }


def normalize_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Map heterogeneous traffic labels into the canonical 0/1/2 encoding."""
    out = df.copy()
    mapping = {
        "0": 0,
        "1": 1,
        "2": 2,
        "normal": 0,
        "direct": 0,
        "benign": 0,
        "non_tor": 0,
        "nontor": 0,
        "non-tor": 0,
        "non-vpn": 0,
        "non_vpn": 0,
        "nonvpn": 0,
        "vpn": 1,
        "openvpn": 1,
        "wireguard": 1,
        "tor": 2,
        "tunnel": 1,
    }
    traffic_class = out.get("traffic_class")
    if traffic_class is None:
        if "label" in out.columns:
            traffic_class = out["label"]
        else:
            raise ValueError(
                "Input DataFrame must include a traffic_class or label column."
            )
    normalized_values = traffic_class.astype(str).str.strip().str.lower().map(mapping)
    if normalized_values.isna().any():
        unknown = sorted(
            set(normalized_values[normalized_values.isna()].index.tolist())
        )
        raise ValueError(f"Unrecognized traffic labels found at indices: {unknown}")
    out["label"] = normalized_values.astype(int)
    return out


def canonicalize_application_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize application names into shared categories for train/test grouping."""
    out = df.copy()
    category_col = "application_category"
    if category_col not in out.columns:
        if "application" in out.columns:
            category_col = "application"
        else:
            raise ValueError(
                "Input DataFrame must include application_category or application."
            )

    mapping = {
        "browsing": "browsing",
        "web": "browsing",
        "browser": "browsing",
        "streaming": "streaming",
        "audio": "streaming",
        "video": "streaming",
        "chat": "chat",
        "email": "email",
        "file_transfer": "file_transfer",
        "ftp": "file_transfer",
        "voip": "voip",
        "p2p": "p2p",
    }
    out["application_category"] = (
        out[category_col].astype(str).str.strip().str.lower().map(mapping)
    )
    out["application_category"] = out["application_category"].fillna("unknown")
    return out


def prepare_historical_dataset(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Standardize labels, fix application categories, and retain metadata useful for splitting."""
    out = raw_df.copy()
    out = normalize_labels(out)
    out = canonicalize_application_categories(out)
    if "traffic_class" not in out.columns:
        out["traffic_class"] = out["label"].map({0: "normal", 1: "vpn", 2: "tor"})
    return out


def select_model_features(df: pd.DataFrame, include_metadata: bool = True) -> list[str]:
    """Return columns intended for model training while excluding leakage-prone identifiers."""
    numeric_cols = [
        c
        for c in df.columns
        if not is_identifier_column(c) and pd.api.types.is_numeric_dtype(df[c])
    ]
    if include_metadata:
        metadata_cols = [
            "application_category",
            "capture_session",
            "dataset_source",
            "capture_year",
            "traffic_class",
        ]
        return [c for c in numeric_cols if c not in {"label"}] + metadata_cols
    return [c for c in numeric_cols if c not in {"label"}]


def split_by_session(
    df: pd.DataFrame, test_session_ids: Iterable[str] | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simple session-wise split helper used in baseline experiments."""
    if "capture_session" not in df.columns or df["capture_session"].isna().any():
        raise ValueError("Real, non-null capture_session IDs are required.")

    if test_session_ids is None:
        sessions = sorted(df["capture_session"].unique())
        test_session_ids = [sessions[0]] if len(sessions) > 0 else []

    test = df[df["capture_session"].isin(test_session_ids)].copy()
    train = df[~df["capture_session"].isin(test_session_ids)].copy()
    return train, test
