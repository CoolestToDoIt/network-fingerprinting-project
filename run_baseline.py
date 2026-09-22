from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from network_fingerprinting.pipeline import run_baseline_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the baseline VPN/Tor classification experiment.")
    parser.add_argument("csv_path", type=str, help="Path to a CSV file containing flow-level traffic records.")
    parser.add_argument("--output", type=str, default=None, help="Optional path to a JSON file for metrics output.")
    args = parser.parse_args()

    data = pd.read_csv(args.csv_path)
    result = run_baseline_experiment(data)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Saved metrics to {out_path}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
