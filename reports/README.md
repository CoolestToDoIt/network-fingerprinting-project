# Start here: project results

Read [the current VPN findings](vpn_study/findings.md) first. They describe the
expanded two-model study and its limitations. The earlier progress update includes
an initial experiment followed by a dated follow-up; use the expanded study for
current numbers.

## Files to read

| File | What it explains |
| --- | --- |
| [VPN findings](vpn_study/findings.md) | Methods, results, error patterns, and limits |
| [Readable results table](vpn_study/summary_readable.md) | All four metrics for both models across five runs |
| [Readable class errors](vpn_study/class_errors_readable.md) | How often each class is identified or mistaken for the other |
| [Comparison figure](vpn_study/comparison.png) | Accuracy and macro-F1 with run variation |
| [Confusion matrices](vpn_study/confusion_matrices.png) | Correct and incorrect predictions by class |
| [Dataset audit](dataset_compatibility.md) | Labels, duplicate rows, overlap, and unresolved feature compatibility |
| [Tor inspection](tor_inspection_2026-10-05.md) | Separate preliminary Tor/NonTor baseline |
| [Collection protocol](modern_collection_protocol.md) | Modern traffic pilot, metadata, and deadlines |
| [Progress update](progress_2026-10-05.md) | Initial milestones and the completed follow-up |

## Terms used in the results

- **Flow:** traffic grouped into a network conversation by a flow extractor.
- **Direct / Non-VPN:** traffic without the VPN label. Tor's NonTor label is a
  separate task and does not prove that the traffic is also Non-VPN.
- **Baseline:** a random split of flows, with both transport classes in training
  and testing. Related flows may still appear on both sides.
- **LOAO:** leave one application category out. Train on six categories and test
  on the seventh. Here it holds out categories, not individual applications.
- **Accuracy:** fraction of test flows classified correctly.
- **Precision:** among predictions of a class, the fraction that are correct.
- **Recall:** among actual flows of a class, the fraction identified correctly.
- **F1:** a score combining precision and recall.
- **Macro:** calculate a score separately for each class, then average them equally.
  This helps expose poor performance on a less common class.
- **Bootstrap:** sample training flows with replacement; some flows repeat and
  others are omitted. Test flows remain excluded.
- **Seed:** a recorded number controlling random choices so a run can be repeated.
- **Standard deviation (SD):** variation across the five runs. It is not a
  confidence interval over independent capture sessions.
- **Confusion matrix:** rows are actual classes; columns are predicted classes.
  A row-normalized matrix shows fractions within each actual class.
- **SHA-256:** a file fingerprint used to check that a rerun uses the same input.

## Structured result files

CSV files have column headers and can be opened in a text editor or spreadsheet.
JSON files use indentation and retain exact numeric values. Readable Markdown
companions round values for presentation; the CSV/JSON files preserve precision.

In `vpn_study/summary.csv`, `_mean` is the average across five runs and `_std` is
sample standard deviation. `runs.csv` contains one evaluation per row.
`class_errors.csv` contains class-specific correct/error fractions on a 0–1 scale.
`metrics.json` records model settings, dataset fingerprint, feature names, class
counts, metrics and confusion matrices. `full_training_reference.json` contains
controls that use all training flows without bootstrap resampling.

For VPN matrices, labels `[0, 1]` mean `[Non-VPN, VPN]`. For the separate Tor
baseline, `[0, 2]` mean `[NonTor, Tor]`. Counts and prediction arrays follow this
encoding. Large generated prediction files live under `data/processed/` and are
indented, but are easier to inspect through the compact reports.

Raw CSV/ARFF data retains the source's headers and labels. ZIP archives and PNG/PDF
figures are binary formats: extract or open them in the appropriate viewer.

Regenerate readable tables after changing results:

```bash
.venv/bin/python render_results.py
```

## Graphics gallery

Open [the graphics gallery](vpn_study/graphics.md) to see the labeled accuracy
chart, accuracy/macro-F1 comparison, and confusion matrices together. PNGs are
suitable for slides; PDF versions are available for reports.
