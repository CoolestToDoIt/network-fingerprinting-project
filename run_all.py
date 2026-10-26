"""Reproduce the current historical study, figures, models, and validation."""

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip full-data model artifacts; experiment evaluation is unchanged.",
    )
    args = parser.parse_args()
    commands = [
        ["-m", "pytest", "-q"],
        ["prepare_datasets.py"],
        ["run_completion_study.py"],
        ["summarize_completion.py"],
        ["validate_results.py"],
    ]
    if not args.skip_models:
        commands.append(["freeze_models.py"])
    for command in commands:
        print("Running: " + " ".join([sys.executable, *command]), flush=True)
        subprocess.run([sys.executable, *command], check=True)
    print(
        "Historical study complete. No modern-data or session-generalization result is implied."
    )


if __name__ == "__main__":
    main()
