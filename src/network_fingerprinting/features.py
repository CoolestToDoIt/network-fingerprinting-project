"""Optional derived features for genuine directional packet and byte counts.

Historical IAT sums and byte rates are not aliases for packet/byte counts.
Native historical experiments bypass this helper and use source numeric columns.
"""

from __future__ import annotations

import pandas as pd

from .data_processing import LEAKAGE_COLUMNS, is_identifier_column


def build_flow_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute ratios only when actual count columns are supplied.

    Zero-duration rates are left missing, rather than replacing duration with an
    invented one-second interval. Capture and application metadata remain available
    for splitting; predictive feature selection excludes them later.
    """
    out = df.copy()
    out = out.drop(
        columns=[
            c
            for c in out
            if is_identifier_column(c)
            and c.strip().lower().replace(" ", "_") in LEAKAGE_COLUMNS
        ],
        errors="ignore",
    )
    required = [
        "flow_duration",
        "total_fwd_packets",
        "total_bwd_packets",
        "total_fwd_bytes",
        "total_bwd_bytes",
    ]
    missing = [column for column in required if column not in out]
    if missing:
        raise ValueError(
            f"Missing genuine flow counts: {missing}. IAT sums and rates cannot substitute for counts."
        )
    for column in required:
        out[column] = pd.to_numeric(out[column], errors="raise")
        if (out[column].dropna() < 0).any():
            raise ValueError(f"Negative flow count or duration: {column}")
    duration = out["flow_duration"].replace(0, float("nan"))
    total_bytes = out["total_fwd_bytes"] + out["total_bwd_bytes"]
    total_packets = out["total_fwd_packets"] + out["total_bwd_packets"]
    out["bytes_per_second"] = total_bytes / duration
    out["packets_per_second"] = total_packets / duration
    out["forward_byte_ratio"] = out["total_fwd_bytes"] / total_bytes.replace(
        0, float("nan")
    )
    out["backward_byte_ratio"] = out["total_bwd_bytes"] / total_bytes.replace(
        0, float("nan")
    )
    out["packet_ratio"] = out["total_fwd_packets"] / total_packets.replace(
        0, float("nan")
    )
    return out
