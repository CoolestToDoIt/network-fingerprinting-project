# Current historical results

Start with [findings and figures](findings.md) or the [research report draft](../final_report_draft.md).

| Artifact | Meaning |
| --- | --- |
| `metrics.json` | All 198 compact evaluation records, environment, configuration, input/source hashes |
| `runs.csv` | One evaluation per row; requested aggregate metrics and partition sizes |
| `matched_summary.csv` | Means and standard deviations for seen/unseen conditions |
| `paired_runs.csv` | Seen/unseen macro-F1 and their difference per model, seed and category |
| `paired_summary.csv` | Means and standard deviations of paired category results |
| `baseline_summary.csv` | Repeated VPN feature-group and Tor random/group baselines |
| `duration_ablation.csv` | Native vs duration-column-removed full-category LOAO at seed 42 |
| `dataset_quality.json` | Counts, missing values, duplicates, input hashes and provenance limits |
| `validation.json` | Independent metric arithmetic and recorded split-invariant checks |

`category_seen` includes target-category training flows; `category_unseen` excludes
that category entirely. Both conditions test identical held-out rows and train on
equal numbers of flows. Exact test feature vectors are purged from both training
sets. A positive macro-F1 drop means the unseen model performs worse.

`feature_group_baseline` groups identical numeric vectors; those groups are not
capture sessions. Tor's `baseline` is a random split. `loao` rows here are the
full-category native/duration ablation; the five-run training-bootstrap LOAO study
is in `../vpn_study/` and uses a different protocol.

For each metric, `_mean` is the arithmetic mean across five splits and `_std` is
the sample standard deviation. Values are fractions on a 0–1 scale except where
readable tables explicitly show percentages. Native/duration ablations use one
seed and do not estimate run variability.

Confusion matrix rows are actual labels; columns are predictions. VPN uses
`[0, 1]` = `[Non-VPN, VPN]`; Tor uses `[0, 2]` = `[NonTor, Tor]`. The `per_class`
object contains precision, recall, F1 and support under those numeric keys. The
majority baseline always chooses the most common **training** class.

Large indented prediction arrays are saved in local ignored checkpoint files at
`data/processed/completion_study/<run_signature_prefix>/`. Row fingerprints compare
membership within a loaded dataset; they are not session IDs or cross-dataset joins.

## Graphics

- [Matched macro-F1 comparison](matched_comparison.png) · [PDF](matched_comparison.pdf)
- [Generalization drops](generalization_drop.png) · [PDF](generalization_drop.pdf)
- [Tor baselines](tor_baselines.png) · [PDF](tor_baselines.pdf)

All values are historical data results. No figure represents real temporal or
session-disjoint testing. Read the limitations in [the findings](findings.md).
