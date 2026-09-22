import pandas as pd

from network_fingerprinting.data_processing import normalize_labels
from network_fingerprinting.features import build_flow_features
from network_fingerprinting.pipeline import run_baseline_experiment


def test_normalize_labels_maps_common_labels_to_target_classes():
    df = pd.DataFrame(
        {
            "traffic_class": ["normal", "VPN", "Tor", "direct", "openvpn", "tor"],
            "application_category": ["browsing", "chat", "streaming", "email", "voip", "p2p"],
        }
    )

    out = normalize_labels(df)

    assert set(out["label"].unique()) == {0, 1, 2}
    assert out["label"].tolist() == [0, 1, 2, 0, 1, 2]


def test_build_flow_features_removes_leakage_and_keeps_relevant_metadata():
    df = pd.DataFrame(
        {
            "src_ip": ["10.0.0.1", "10.0.0.2", "10.0.0.1", "10.0.0.2"],
            "dst_ip": ["8.8.8.8", "1.1.1.1", "8.8.8.8", "1.1.1.1"],
            "flow_duration": [1.0, 2.0, 3.0, 4.0],
            "total_fwd_packets": [10, 20, 30, 40],
            "total_bwd_packets": [8, 9, 11, 12],
            "total_fwd_bytes": [100, 200, 300, 400],
            "total_bwd_bytes": [80, 90, 110, 120],
            "application_category": ["browsing", "chat", "streaming", "browsing"],
            "capture_session": ["s1", "s2", "s3", "s4"],
        }
    )

    out = build_flow_features(df)

    assert "src_ip" not in out.columns
    assert "dst_ip" not in out.columns
    assert "flow_duration" in out.columns
    assert "bytes_per_second" in out.columns
    assert "application_category" in out.columns
    assert "capture_session" in out.columns


def test_run_baseline_experiment_returns_metrics_and_predictions():
    rows = []
    for label, base in [(0, 10), (1, 20), (2, 30)]:
        for i in range(30):
            rows.append(
                {
                    "flow_duration": base + i,
                    "total_fwd_packets": base + i,
                    "total_bwd_packets": max(1, base // 2 + i),
                    "total_fwd_bytes": (base + i) * 100,
                    "total_bwd_bytes": (base + i) * 80,
                    "src_ip": f"10.0.0.{i}",
                    "dst_ip": f"8.8.8.{i}",
                    "application_category": ["browsing", "chat", "streaming"][label],
                    "capture_session": f"session_{label}_{i}",
                    "traffic_class": ["normal", "vpn", "tor"][label],
                }
            )

    df = pd.DataFrame(rows)
    result = run_baseline_experiment(df)

    assert result["accuracy"] >= 0.7
    assert "macro_f1" in result
    assert "macro_precision" in result
    assert "macro_recall" in result
    assert "n_test_samples" in result
    assert len(result["predictions"]) == result["n_test_samples"]
