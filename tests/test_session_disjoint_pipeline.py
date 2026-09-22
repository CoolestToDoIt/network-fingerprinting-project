import pandas as pd

from network_fingerprinting.pipeline import run_session_disjoint_experiment


def test_run_session_disjoint_experiment_keeps_sessions_out_of_both_splits():
    rows = []
    for session in range(12):
        for label in [0, 1]:
            rows.append(
                {
                    "flow_duration": session * 5 + label,
                    "total_fiat": session + label + 1,
                    "total_biat": session + label + 2,
                    "class1": "VPN" if label == 1 else "Non-VPN",
                    "capture_session": f"session_{session}",
                    "traffic_class": "vpn" if label == 1 else "non-vpn",
                    "label": label,
                }
            )

    df = pd.DataFrame(rows)
    result = run_session_disjoint_experiment(df)

    train_sessions = set(result["train_sessions"])
    test_sessions = set(result["test_sessions"])
    assert train_sessions.isdisjoint(test_sessions)
    assert len(result["predictions"]) == result["n_test_samples"]
    assert result["n_test_samples"] > 0
    assert "accuracy" in result
