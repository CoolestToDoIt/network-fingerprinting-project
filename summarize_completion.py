"""Generate readable tables and figures for the stricter historical study."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/network-fingerprinting-mpl")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path("reports/completion_study")
MODELS = {
    "logistic_regression": "Logistic regression",
    "random_forest": "Random Forest",
}
CATEGORIES = ["browsing", "chat", "email", "file_transfer", "p2p", "streaming", "voip"]
NAMES = ["Browsing", "Chat", "Email", "File transfer", "P2P", "Streaming", "VoIP"]


def markdown_table(headers, rows):
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        + ["| " + " | ".join(map(str, row)) + " |" for row in rows]
    )


def save_figure(figure, name):
    figure.savefig(ROOT / f"{name}.png", dpi=180)
    figure.savefig(ROOT / f"{name}.pdf")
    plt.close(figure)


def main():
    report = json.loads((ROOT / "metrics.json").read_text())
    runs = pd.DataFrame(report["results"])
    runs["dataset"] = runs.run_id.str.split("_").str[0]
    matched = runs[runs.experiment == "matched_category"]
    metrics = ["accuracy", "macro_f1", "macro_precision", "macro_recall"]
    summary = matched.groupby(["model", "held_out_category", "condition"])[metrics].agg(
        ["mean", "std"]
    )
    summary.columns = ["_".join(column) for column in summary.columns]
    summary.reset_index().to_csv(ROOT / "matched_summary.csv", index=False)
    pairs = matched.pivot(
        index=["model", "seed", "held_out_category"],
        columns="condition",
        values="macro_f1",
    )
    pairs["macro_f1_drop"] = pairs.category_seen - pairs.category_unseen
    pairs.reset_index().to_csv(ROOT / "paired_runs.csv", index=False)
    drops = pairs.groupby(["model", "held_out_category"]).agg(["mean", "std"])
    drops.columns = ["_".join(column) for column in drops.columns]
    drops.reset_index().to_csv(ROOT / "paired_summary.csv", index=False)
    table_rows = []
    for model in MODELS:
        for category, label in zip(CATEGORIES, NAMES):
            row = drops.loc[(model, category)]
            table_rows.append(
                [
                    MODELS[model],
                    label,
                    f"{row.category_seen_mean:.3f}",
                    f"{row.category_unseen_mean:.3f}",
                    f"{row.macro_f1_drop_mean:+.3f} ± {row.macro_f1_drop_std:.3f}",
                ]
            )
    baseline = runs[runs.experiment.isin(["baseline", "feature_group_baseline"])]
    baseline_summary = baseline.groupby(["dataset", "experiment", "model"])[
        metrics
    ].agg(["mean", "std"])
    baseline_summary.columns = ["_".join(column) for column in baseline_summary.columns]
    baseline_summary.reset_index().to_csv(ROOT / "baseline_summary.csv", index=False)
    baseline_rows = []
    for (dataset, experiment, model), row in baseline_summary.iterrows():
        baseline_rows.append(
            [
                dataset.upper(),
                "Random" if experiment == "baseline" else "Exact-feature-group split",
                MODELS[model],
                f"{100*row.accuracy_mean:.2f}% ± {100*row.accuracy_std:.2f} pp",
                f"{row.macro_f1_mean:.3f} ± {row.macro_f1_std:.3f}",
            ]
        )
    ablation = runs[runs.experiment == "loao"].pivot(
        index=["model", "held_out_category"], columns="feature_set", values="macro_f1"
    )
    ablation["change_without_duration"] = ablation.without_duration - ablation.native
    ablation.reset_index().to_csv(ROOT / "duration_ablation.csv", index=False)
    ablation_rows = [
        [
            MODELS[model],
            category.replace("_", " "),
            f"{row.native:.3f}",
            f"{row.without_duration:.3f}",
            f"{row.change_without_duration:+.3f}",
        ]
        for (model, category), row in ablation.iterrows()
    ]
    overview = "# Historical validation results — October 26, 2026\n\n"
    overview += f"{len(runs)} model evaluations. All numbers below come from `metrics.json`.\n\n"
    overview += "## Same test flows, equal training sizes\n\n"
    overview += (
        "Each category has five paired tests. Both models see the exact same test rows per seed. "
        "The seen condition includes other flows from the test category in training; the unseen "
        "condition excludes the category entirely. Training row counts are equal and exact test "
        "feature vectors are purged from both training sets. Drop = seen macro-F1 minus unseen "
        "macro-F1. Standard deviations describe variation across five splits, not independent sessions.\n\n"
    )
    overview += (
        markdown_table(
            ["Model", "Test category", "Seen F1", "Unseen F1", "Drop, mean ± SD"],
            table_rows,
        )
        + "\n\n"
    )
    overview += "![Paired macro-F1 comparison](matched_comparison.png)\n\n"
    overview += "![Macro-F1 drops](generalization_drop.png)\n\n"
    overview += "## VPN and Tor baselines\n\n"
    overview += (
        "Exact-feature-group splits keep identical numeric feature vectors together. "
        "They are not session-disjoint splits. VPN random baselines remain in `../vpn_study/`. "
        "Tor NonTor is a separate label from VPN direct; scores are not comparable tasks.\n\n"
    )
    overview += (
        markdown_table(
            [
                "Dataset",
                "Evaluation",
                "Model",
                "Accuracy, mean ± SD",
                "Macro-F1, mean ± SD",
            ],
            baseline_rows,
        )
        + "\n\n"
    )
    overview += "![Tor baseline comparison](tor_baselines.png)\n\n"
    overview += "## Duration ablation (one seed, full-category LOAO)\n\n"
    overview += (
        "This removes only the raw duration column. IAT/rate features can still encode duration-related "
        "information; it is not a complete timing ablation or a tuned feature selection result.\n\n"
    )
    overview += (
        markdown_table(
            ["Model", "Category", "Native F1", "Without duration F1", "Change"],
            ablation_rows,
        )
        + "\n\n"
    )
    overview += (
        "## Interpretation limits\n\nNo real modern traffic or historical session IDs were available. "
        "Training-set composition changes between matched conditions even when row counts match. "
        "Correlated flows can remain. Exact duplicate-vector grouping does not establish capture independence. "
        "No confidence intervals or significance tests over independent sessions are claimed. "
        "Per-class metrics, majority-class baselines, confusion matrices and split fingerprints are in `metrics.json`.\n"
    )
    (ROOT / "findings.md").write_text(overview)
    figure, axes = plt.subplots(
        1, 2, figsize=(13, 5.5), sharey=True, layout="constrained"
    )
    for axis, (model, title) in zip(axes, MODELS.items()):
        for index, (condition, label, color) in enumerate(
            [
                ("category_seen", "Category seen", "#2878b5"),
                ("category_unseen", "Category unseen", "#e68122"),
            ]
        ):
            rows = (
                summary.loc[(model, slice(None), condition), :]
                .reset_index()
                .set_index("held_out_category")
                .loc[CATEGORIES]
            )
            bars = axis.bar(
                np.arange(7) + (index - 0.5) * 0.36,
                rows.macro_f1_mean,
                width=0.36,
                yerr=rows.macro_f1_std,
                capsize=3,
                color=color,
                label=label,
            )
            axis.bar_label(bars, fmt="%.2f", fontsize=8, padding=4)
        axis.set_xticks(range(7), NAMES, rotation=35, ha="right")
        axis.set_ylim(0, 1.1)
        axis.set_title(title)
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    axes[0].set_ylabel("Macro-F1")
    axes[0].legend(loc="upper left", fontsize=9)
    figure.suptitle(
        "Same test flows: does seeing the application category help?", fontsize=15
    )
    figure.supxlabel(
        "Equal training row counts; exact test feature vectors excluded from training. Error bars = five-split SD.",
        fontsize=9,
    )
    save_figure(figure, "matched_comparison")
    figure, axis = plt.subplots(figsize=(10, 6), layout="constrained")
    for index, (model, label) in enumerate(MODELS.items()):
        rows = drops.loc[model].loc[CATEGORIES]
        axis.barh(
            np.arange(7) + (index - 0.5) * 0.35,
            rows.macro_f1_drop_mean,
            height=0.35,
            xerr=rows.macro_f1_drop_std,
            capsize=3,
            label=label,
        )
    axis.set_yticks(range(7), NAMES)
    axis.invert_yaxis()
    axis.axvline(0, color="black", linewidth=0.8)
    axis.set_xlabel("Macro-F1 drop: category seen − category unseen")
    axis.legend()
    axis.set_title("Largest unseen-category losses: VoIP, P2P, and streaming")
    axis.grid(axis="x", alpha=0.2)
    axis.set_axisbelow(True)
    figure.supxlabel(
        "Same test flows and equal training row counts. Error bars are sample SD across five splits.",
        fontsize=9,
    )
    save_figure(figure, "generalization_drop")
    figure, axes = plt.subplots(1, 2, figsize=(10, 5), layout="constrained")
    tor_summary = baseline_summary.loc["tor"]
    for axis, metric, title in zip(
        axes, ["accuracy", "macro_f1"], ["Accuracy", "Macro-F1"]
    ):
        for index, (experiment, label) in enumerate(
            [
                ("baseline", "Random split"),
                ("feature_group_baseline", "Feature-group split"),
            ]
        ):
            rows = tor_summary.loc[experiment].loc[list(MODELS)]
            bars = axis.bar(
                np.arange(2) + (index - 0.5) * 0.36,
                rows[metric + "_mean"],
                width=0.36,
                yerr=rows[metric + "_std"],
                capsize=3,
                label=label,
            )
            axis.bar_label(bars, fmt="%.3f", padding=4, fontsize=9)
        axis.set_xticks([0, 1], ["Logistic\nregression", "Random Forest"])
        axis.set_ylim(0, 1.12)
        axis.set_title(title)
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    axes[0].legend(fontsize=8, loc="upper left")
    figure.suptitle("Tor vs NonTor: strong within-dataset performance", fontsize=14)
    figure.supxlabel(
        "Five-split means ± SD. Grouping exact feature vectors does not establish session independence.",
        fontsize=9,
    )
    save_figure(figure, "tor_baselines")
    print("Saved readable findings, CSV summaries and six PNG/PDF figures.")


if __name__ == "__main__":
    main()
