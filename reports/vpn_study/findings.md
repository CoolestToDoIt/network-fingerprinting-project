# VPN generalization study — October 5, 2026

## Design

Two models, five seeds (42–46), and eight evaluations per model/seed: 80 runs.
Exact duplicates are removed before splitting (18,758 → 18,074 flows). The model
feature set is the same 23 native numeric columns for both models. Imputation
and scaling are fitted on training only. No hyperparameter search was conducted.
Random Forest uses 200 trees and minimum leaf size 2; logistic regression uses
default regularization and maximum 3,000 iterations.

Random baseline: stratified 75/25 splits vary across seeds. LOAO: test on all
flows from one category; train on the other six, bootstrapped with replacement
within category and transport class at the original stratum size. Held-out flows
never enter training. Models use matched splits/resamples per seed. The bootstrap
contains fewer unique training flows than the full training set; full-training
seed-42 LOAO controls are saved separately to check this effect.

These standard deviations describe split/resampling/estimator sensitivity.
They are not confidence intervals over independent capture sessions, nor a
pure measure of temporal or session generalization. LOAO categories have different
test populations and class balances. Random baseline and LOAO drops are descriptive
rather than paired causal estimates.

## Measured results

| Model | Evaluation | Accuracy, mean ± SD | Macro-F1, mean ± SD |
| --- | --- | ---: | ---: |
| logistic regression | baseline | 61.70% ± 1.57 pp | 0.6037 ± 0.0151 |
| logistic regression | browsing | 52.96% ± 0.46 pp | 0.4500 ± 0.0248 |
| logistic regression | chat | 50.24% ± 0.35 pp | 0.4133 ± 0.0075 |
| logistic regression | email | 60.93% ± 1.53 pp | 0.3785 ± 0.0060 |
| logistic regression | file transfer | 52.41% ± 3.40 pp | 0.5206 ± 0.0311 |
| logistic regression | p2p | 37.00% ± 1.71 pp | 0.2938 ± 0.0268 |
| logistic regression | streaming | 49.25% ± 1.45 pp | 0.4920 ± 0.0142 |
| logistic regression | voip | 29.13% ± 0.06 pp | 0.2257 ± 0.0004 |
| random forest | baseline | 92.45% ± 0.24 pp | 0.9243 ± 0.0023 |
| random forest | browsing | 61.83% ± 1.68 pp | 0.6125 ± 0.0180 |
| random forest | chat | 66.87% ± 2.99 pp | 0.6152 ± 0.0425 |
| random forest | email | 65.70% ± 1.15 pp | 0.5781 ± 0.0206 |
| random forest | file transfer | 70.45% ± 1.24 pp | 0.6614 ± 0.0175 |
| random forest | p2p | 43.78% ± 1.08 pp | 0.4177 ± 0.0152 |
| random forest | streaming | 46.14% ± 2.27 pp | 0.4463 ± 0.0240 |
| random forest | voip | 57.96% ± 3.73 pp | 0.4442 ± 0.0837 |

## Full-training controls

Without training bootstrapping, Random Forest LOAO accuracy still ranges from
43.68% (P2P) to 71.09% (file transfer) at seed 42. Thus the poor category transfer
is also present when using every available training flow. This control does not
resolve the differing class balances, test populations, or capture correlations.

## Error analysis

Random Forest achieves 92.45% baseline accuracy (macro-F1 0.9243), but its
LOAO mean accuracy ranges from 43.78% (P2P) to 70.45% (file transfer). A stronger
random-split model does not eliminate poor held-out-category performance.

- Random Forest P2P: direct recall 21.62%, VPN recall 75.11%; many direct flows
  are called VPN.
- Random Forest streaming: VPN recall 29.09%, direct recall 64.13%; many VPN
  flows are called direct.
- Random Forest VoIP: direct recall 95.69%, VPN recall 10.99%. Accuracy of 57.96%
  conceals poor VPN sensitivity; macro-F1 is only 0.4442.
- Logistic regression email: direct recall 0%, VPN recall 94.49%. Accuracy of
  60.93% therefore should not be interpreted as useful balanced classification.

These are mean class recalls over fixed LOAO test flows. They establish error
patterns, not why those patterns occur. Training resampling SD is especially
large for Random Forest VoIP macro-F1 (0.0837), which deserves investigation.

## Limits and next steps

Exact deduplication leaves correlated flows and repeated numeric vectors. Genuine
session-disjoint validation is unavailable without capture provenance. Prior
single-run results did not deduplicate VPN rows and must not be directly compared
to this revised study as if only the model changed. Protocols, flow statistics,
class balances and capture conditions may influence results.

Use the compatibility audit before merging VPN/Tor or scoring modern traffic.
Proceed with one modern paired-capture pilot and stop data/provenance investigation
by October 19 if it cannot support credible evaluation. Keep the completed VPN
study as the core deliverable and the Tor baseline as secondary.

## Artifacts and reproduction

- `summary.csv`: means and sample standard deviations.
- `runs.csv` and `metrics.json`: per-run metrics, labels, features, counts and hashes.
- `class_errors.csv`: mean row-normalized class errors.
- `full_training_reference.json`: non-bootstrapped controls.
- `comparison.png` / `.pdf`: accuracy and macro-F1 figure.
- `confusion_matrices.png` / `.pdf`: row-normalized confusion matrices.
- `data/processed/vpn_study/predictions.json`: predictions and true labels.

```bash
.venv/bin/python run_repeated_study.py 'data/raw/Scenario B-ARFF.zip'
.venv/bin/python plot_study.py
```
