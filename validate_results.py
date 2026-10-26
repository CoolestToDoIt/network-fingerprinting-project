"""Independently check saved study arithmetic and scientific split invariants."""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
)


def validate_result(result):
    matrix = np.asarray(result["confusion_matrix"])
    labels = result["confusion_matrix_labels"]
    assert matrix.shape == (len(labels), len(labels)), "Confusion matrix shape mismatch"
    assert (matrix >= 0).all(), "Negative confusion count"
    assert matrix.sum() == result["n_test_samples"], "Confusion total mismatch"
    actual = np.repeat(np.asarray(labels), matrix.sum(axis=1))
    predicted = np.concatenate([np.repeat(np.asarray(labels), row) for row in matrix])
    assert np.isclose(accuracy_score(actual, predicted), result["accuracy"])
    for name, metric in [
        ("macro_f1", f1_score),
        ("macro_precision", precision_score),
        ("macro_recall", recall_score),
    ]:
        assert np.isclose(
            metric(actual, predicted, labels=labels, average="macro", zero_division=0),
            result[name],
        ), name
    if "predictions" in result:
        assert (
            len(result["predictions"])
            == len(result["true_labels"])
            == result["n_test_samples"]
        )
        assert np.array_equal(
            confusion_matrix(
                result["true_labels"], result["predictions"], labels=labels
            ),
            matrix,
        )
    if result.get("condition") == "category_unseen":
        assert result["held_out_category"] not in result["train_categories"]
    if "feature_group_overlap" in result:
        assert result["feature_group_overlap"] == 0


def main():
    root = Path("reports/completion_study")
    report = json.loads((root / "metrics.json").read_text())
    assert len(report["results"]) == 198, "Incomplete final study"
    paired = {}
    for result in report["results"]:
        validate_result(result)
        if result["experiment"] == "matched_category":
            key = (result["model"], result["seed"], result["held_out_category"])
            paired.setdefault(key, {})[result["condition"]] = result
    assert len(paired) == 70
    for pair in paired.values():
        seen, unseen = pair["category_seen"], pair["category_unseen"]
        assert seen["test_fingerprint"] == unseen["test_fingerprint"]
        assert seen["n_train_samples"] == unseen["n_train_samples"]
        assert seen["test_class_counts"] == unseen["test_class_counts"]
    checkpoint = Path("data/processed/completion_study") / report["run_signature"][:16]
    detailed_count = 0
    for path in checkpoint.glob("*.json"):
        for result in json.loads(path.read_text()):
            validate_result(result)
            detailed_count += 1
    assert detailed_count == 198, "Missing prediction checkpoints"
    verification = {
        "evaluations_checked": 198,
        "paired_comparisons_checked": 70,
        "predictions_checked": detailed_count,
        "status": "passed",
        "limits": "Checks arithmetic and recorded split invariants; cannot establish real-session independence.",
    }
    (root / "validation.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
