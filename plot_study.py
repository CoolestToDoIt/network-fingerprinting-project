"""Render report figures from compact study results, without retraining."""

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/network-fingerprinting-mpl")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    root = Path("reports/vpn_study")
    summary = pd.read_csv(root / "summary.csv")
    categories = [
        "baseline",
        "browsing",
        "chat",
        "email",
        "file_transfer",
        "p2p",
        "streaming",
        "voip",
    ]
    figure, axes = plt.subplots(2, 1, figsize=(11, 8), layout="constrained")
    for axis, metric in zip(axes, ["accuracy", "macro_f1"]):
        for model_index, (model, label) in enumerate(
            [
                ("logistic_regression", "Logistic regression"),
                ("random_forest", "Random Forest"),
            ]
        ):
            model_summary = (
                summary[summary.model == model]
                .set_index("held_out_category")
                .loc[categories]
            )
            axis.bar(
                np.arange(8) + (model_index - 0.5) * 0.36,
                model_summary[metric + "_mean"],
                width=0.36,
                yerr=model_summary[metric + "_std"],
                capsize=3,
                label=label,
            )
        axis.set_ylim(0, 1)
        axis.set_ylabel(metric.replace("_", " ").title())
        axis.set_xticks(np.arange(8), [c.replace("_", " ").title() for c in categories])
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    axes[0].legend(loc="upper right")
    figure.suptitle(
        "VPN classification: random baseline and category-held-out evaluation\nFive runs; bars = mean, error bars = sample standard deviation",
        fontsize=13,
    )
    figure.savefig(root / "comparison.png", dpi=180)
    figure.savefig(root / "comparison.pdf")
    plt.close(figure)
    results = json.loads((root / "metrics.json").read_text())["results"]
    # Average row-normalized matrices; counts are retained per run in JSON.
    figure, axes = plt.subplots(2, 8, figsize=(18, 5.5), layout="constrained")
    error_rows = []
    for model_index, model in enumerate(["logistic_regression", "random_forest"]):
        for category_index, category in enumerate(categories):
            matrices = [
                np.asarray(result["confusion_matrix"], dtype=float)
                for result in results
                if result["model"] == model and result["held_out_category"] == category
            ]
            normalized = np.stack(
                [matrix / matrix.sum(axis=1, keepdims=True) for matrix in matrices]
            )
            mean_matrix = normalized.mean(axis=0)
            axis = axes[model_index, category_index]
            axis.imshow(mean_matrix, vmin=0, vmax=1, cmap="Blues")
            for row in range(2):
                for col in range(2):
                    axis.text(
                        col,
                        row,
                        f"{mean_matrix[row,col]:.2f}",
                        ha="center",
                        va="center",
                        color="white" if mean_matrix[row, col] > 0.55 else "black",
                    )
            axis.set_xticks([0, 1], ["Direct", "VPN"], fontsize=8)
            axis.set_yticks([0, 1], ["Direct", "VPN"], fontsize=8)
            if model_index == 0:
                axis.set_title(category.replace("_", " "), fontsize=10)
            if category_index == 0:
                axis.set_ylabel(model.replace("_", " ") + "\nActual", fontsize=10)
            axis.set_xlabel("Predicted", fontsize=8)
            error_rows.append(
                {
                    "model": model,
                    "category": category,
                    "direct_recall": mean_matrix[0, 0],
                    "vpn_recall": mean_matrix[1, 1],
                    "direct_as_vpn": mean_matrix[0, 1],
                    "vpn_as_direct": mean_matrix[1, 0],
                }
            )
    figure.suptitle(
        "Mean row-normalized confusion matrices across five runs", fontsize=14
    )
    figure.savefig(root / "confusion_matrices.png", dpi=180)
    figure.savefig(root / "confusion_matrices.pdf")
    plt.close(figure)
    pd.DataFrame(error_rows).to_csv(root / "class_errors.csv", index=False)


if __name__ == "__main__":
    main()
