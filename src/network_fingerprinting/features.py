from __future__ import annotations

import pandas as pd


def build_flow_features(df: pd.DataFrame) -> pd.DataFrame:
    """Construct a compact flow feature matrix with common leakage fields removed."""
    out = df.copy()
    leakage = {"src_ip", "dst_ip", "source_ip", "destination_ip", "src_port", "dst_port", "application_name"}
    out = out.drop(columns=[c for c in leakage if c in out.columns], errors="ignore")

    feature_aliases = {
        "flow_duration": ["duration", "flow_duration"],
        "total_fwd_packets": ["total_fiat", "total_fwd_packets"],
        "total_bwd_packets": ["total_biat", "total_bwd_packets"],
        "total_fwd_bytes": ["flowBytesPerSecond", "total_fwd_bytes"],
        "total_bwd_bytes": ["flowBytesPerSecond", "total_bwd_bytes"],
    }

    for canonical, aliases in feature_aliases.items():
        for alias in aliases:
            if alias in out.columns:
                out[canonical] = pd.to_numeric(out[alias], errors="coerce")
                break

    if "flow_duration" not in out.columns and "duration" in out.columns:
        out["flow_duration"] = pd.to_numeric(out["duration"], errors="coerce")

    if "total_fwd_bytes" not in out.columns and "flowBytesPerSecond" in out.columns:
        out["total_fwd_bytes"] = pd.to_numeric(out["flowBytesPerSecond"], errors="coerce") * out["flow_duration"].replace(0, 1)

    if "total_bwd_bytes" not in out.columns and "flowBytesPerSecond" in out.columns:
        out["total_bwd_bytes"] = pd.to_numeric(out["flowBytesPerSecond"], errors="coerce") * out["flow_duration"].replace(0, 1)

    if "total_fwd_bytes" not in out.columns and "total_fwd_packets" in out.columns:
        out["total_fwd_bytes"] = pd.to_numeric(out["total_fwd_packets"], errors="coerce")

    if "total_bwd_bytes" not in out.columns and "total_bwd_packets" in out.columns:
        out["total_bwd_bytes"] = pd.to_numeric(out["total_bwd_packets"], errors="coerce")

    required = [
        "flow_duration",
        "total_fwd_packets",
        "total_bwd_packets",
        "total_fwd_bytes",
        "total_bwd_bytes",
    ]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required flow features: {missing}")

    out["bytes_per_second"] = out["total_fwd_bytes"] / out["flow_duration"].replace(0, 1)
    out["packets_per_second"] = (out["total_fwd_packets"] + out["total_bwd_packets"]) / out["flow_duration"].replace(0, 1)
    out["forward_byte_ratio"] = out["total_fwd_bytes"] / (out["total_fwd_bytes"] + out["total_bwd_bytes"]).replace(0, 1)
    out["backward_byte_ratio"] = out["total_bwd_bytes"] / (out["total_fwd_bytes"] + out["total_bwd_bytes"]).replace(0, 1)
    out["packet_ratio"] = out["total_fwd_packets"] / (out["total_fwd_packets"] + out["total_bwd_packets"]).replace(0, 1)
    return out
