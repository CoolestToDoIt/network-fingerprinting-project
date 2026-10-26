# Project status — October 26, 2026

**Target:** December 5, 2026. The historical study and evaluation software are now
substantially complete. Real temporal evidence remains the main unfinished part.

## How to interpret “about three quarters”

Sixteen of the 21 concrete deliverable checkpoints below are implemented and
reviewable: approximately **76% by checkpoint count**. This is a rough readiness
estimate, not an effort-weighted schedule, an instructor-approved scope change,
or a claim that 76% of the research questions have empirical answers. The remaining
data-dependent work is substantial and can dominate the remaining calendar.

| # | Deliverable | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Local package/environment and dependencies | Complete | `pyproject.toml`, reproducible commands |
| 2 | VPN historical loader | Complete | Loader, tests and native feature table |
| 3 | Tor binary loader | Complete | Loader and repeated baselines |
| 4 | Dataset quality/provenance audit | Complete | `reports/completion_study/dataset_quality.json` |
| 5 | Leakage guards and correct feature handling | Complete | Numeric metadata exclusion and regression tests |
| 6 | Two classical models | Complete | Logistic regression and Random Forest |
| 7 | Shared and per-class reporting | Complete | All requested metrics, majority baselines, confusion matrices |
| 8 | All seven VPN category holdouts | Complete | Earlier study and new full-training references |
| 9 | Stronger matched category comparison | Complete | 70 same-test, equal-training-size pairs |
| 10 | Repeat and sensitivity experiments | Complete | Five seeds, feature-group splits, duration ablation |
| 11 | Readable tables and graphics | Complete | PNG/PDF figures, generated Markdown and CSV |
| 12 | Frozen historical model artifacts | Complete | Four local models with readable model cards |
| 13 | Historical-to-modern evaluator | Complete as software | Validated contracts, training-only transforms, synthetic tests |
| 14 | Combined-shift evaluator | Complete as software | Held-out-category training and synthetic tests |
| 15 | Research report draft | Complete as draft | `reports/final_report_draft.md` |
| 16 | Reproduction and saved-result checks | Complete | `run_all.py`, metric/split validation |
| 17 | Compatible real modern dataset | Pending | No modern capture files yet |
| 18 | Real temporal and combined-shift experiments | Pending | Need verified modern data |
| 19 | Real historical session-disjoint evaluation | Pending | No genuine session IDs in exports |
| 20 | Tor category holdouts and pooled three-class analysis | Pending | Missing NonTor categories and feature/provenance alignment |
| 21 | Final revisions, independent reproduction and presentation | Pending | Draft and artifacts ready for review |

## What can be claimed now

The latest study completed 198 evaluations. It includes 140 matched category
condition evaluations (70 comparisons), 20 feature-group baselines, 10 Tor random
baselines, and 28 full-category duration/reference evaluations. It supplements the
earlier 80 repeated VPN evaluations and 14 full-training controls; these counts
represent different analyses, not independent datasets.

On the same category test flows, Random Forest's average macro-F1 is 0.902 with
the category seen and 0.535 with it excluded. Exact test feature vectors are removed
from training and total training row counts match. The result supports a category
generalization gap under this design, not a causal explanation or a deployment claim.

## What cannot be claimed

There is no observed modern-data result, no real session-disjoint result, no Tor
binary category-LOAO result, and no validated normal/VPN/Tor pooled classifier.
Implemented evaluators and synthetic tests do not count as those observations.

The original research scope remains in `PLAN.md`. Separate binary tasks are a
practical current limitation, not a silent replacement of the original objective.
Ask the instructor to approve a reduced final scope if the missing metadata or
modern extraction cannot be resolved. No such approval is assumed here.

## Remaining calendar

1. **October 29:** direct/VPN pilot and extractor review; instructor scope check.
2. **November 2:** feasibility decision and historical experiment freeze.
3. **November 9:** real modern scoring if compatible data exists.
4. **November 16:** revised report with results or clearly documented limits.
5. **November 30:** independent reproduction and presentation complete.
6. **December 5:** submit.

Start with [the latest results](reports/completion_study/findings.md),
[the report draft](reports/final_report_draft.md), and
[the transfer readiness guide](reports/transfer_readiness.md).
