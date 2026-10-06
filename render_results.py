"""Create plain-language Markdown tables from the saved study CSVs."""

from pathlib import Path

import pandas as pd

STUDY_DIRECTORY = Path("reports/vpn_study")
MODEL_NAMES = {
    "logistic_regression": "Logistic regression",
    "random_forest": "Random Forest",
}


def category_name(value):
    if value == "baseline":
        return "Random baseline"
    if value == "voip":
        return "VoIP"
    if value == "p2p":
        return "P2P"
    return str(value).replace("_", " ").capitalize()


def write_table(path, introduction, headers, rows):
    lines = [
        introduction,
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    summary = pd.read_csv(STUDY_DIRECTORY / "summary.csv")
    rows = []
    for _, result in summary.iterrows():
        row = [MODEL_NAMES[result["model"]], category_name(result["held_out_category"])]
        for metric in ["accuracy", "macro_f1", "macro_precision", "macro_recall"]:
            mean, deviation = result[metric + "_mean"], result[metric + "_std"]
            row.append(f"{mean:.3f} ± {deviation:.3f}")
        rows.append(row)
    write_table(
        STUDY_DIRECTORY / "summary_readable.md",
        "# Results across five runs\n\nValues are mean ± sample standard deviation, on a 0–1 scale. "
        "For example, 0.924 accuracy means 92.4% correct. The variation describes run "
        "sensitivity, not confidence intervals over independent sessions. "
        "Held-out rows use training bootstrap samples; the random baseline varies its split.",
        [
            "Model",
            "Evaluation",
            "Accuracy",
            "Macro-F1",
            "Macro-precision",
            "Macro-recall",
        ],
        rows,
    )
    errors = pd.read_csv(STUDY_DIRECTORY / "class_errors.csv")
    rows = []
    for _, result in errors.iterrows():
        rows.append(
            [MODEL_NAMES[result["model"]], category_name(result["category"])]
            + [
                f"{100 * result[column]:.1f}%"
                for column in [
                    "direct_recall",
                    "vpn_recall",
                    "direct_as_vpn",
                    "vpn_as_direct",
                ]
            ]
        )
    write_table(
        STUDY_DIRECTORY / "class_errors_readable.md",
        "# Which class gets misclassified?\n\nDirect means Non-VPN. Each value is the mean "
        "percentage across five runs. Correct and incorrect percentages for each actual "
        "class sum to 100%, apart from rounding.",
        [
            "Model",
            "Evaluation",
            "Direct correctly identified",
            "VPN correctly identified",
            "Direct mistaken for VPN",
            "VPN mistaken for direct",
        ],
        rows,
    )


if __name__ == "__main__":
    main()
