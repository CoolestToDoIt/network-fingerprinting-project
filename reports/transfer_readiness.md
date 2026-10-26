# Temporal and combined-shift evaluation: ready code, missing evidence

Status on October 26, 2026: no modern dataset has been collected. The repository
contains tested transfer evaluation code, but no real temporal score. Synthetic
fixtures in tests verify behavior only and are not research observations.

## Required inputs

The historical and modern CSVs must contain the same explicitly declared feature
columns plus `traffic_class`, `application_category`, `capture_year` and
`dataset_source`. Modern rows also need genuine `capture_session` identifiers.
Session class/category/year must be consistent; years must be strictly later than
historical years. Cross-period sources/sessions must be disjoint. Exact feature
vector overlap is rejected for review, because provenance is otherwise uncertain.

The exported VPN table in `data/processed/historical/vpn.csv` supplies the native
historical schema. Tor has no complete category labels and therefore does not yet
meet the combined-shift input requirements.

## Compatibility contract

Copy `config/transfer_contract.pending.json` to a new file. Its default is
intentionally incomplete and scoring rejects it. Resolve:

1. The historical and modern extractor versions and source references.
2. Feature names, numerical units, and exact definitions. A smaller common feature
   subset is acceptable if it is genuinely compatible; retrain on that subset.
3. Timeout, direction convention, and active/idle rules.
4. A local manually checked extraction fixture report, with its SHA-256 recorded
   in `verification_notes`. The hash checks which evidence was supplied; it does
   not itself prove that a human's compatibility assessment is correct.

Only then mark `compatibility_verified` true. A declaration without actual
verification is not evidence. Current successor CICFlowMeter source is available
through the official dataset link, but its version alone does not establish the
settings used for the historical exports.
[Official source repository](https://github.com/UNBCIC/CICFlowMeter).

## Command when real inputs are available

```bash
.venv/bin/python run_transfer.py data/processed/historical/vpn.csv \
  data/processed/modern/vpn.csv \
  --contract config/transfer_contract.verified.json \
  --model random_forest
```

This fits imputation, scaling and the classifier using historical rows only. It
reports overall, per-category and per-session modern metrics, then fits additional
historical-only models excluding each test category for combined-shift evaluation.
Both classes are required for a combined category result; unusable categories
receive a recorded skip reason. Session metrics use the full task label set, so
macro-F1 on a one-class session should be read with care. Use class recall and
aggregate category metrics as well.

The command saves indented metrics/provenance JSON and local historical model
artifacts under `data/processed/transfer/`. Treat model files as local trusted
artifacts; they are not a substitute for the readable metrics.

No modern-data hyperparameter tuning, preprocessing fitting, automatic feature
renaming, or unit conversions occur. The output is exploratory cross-environment
transfer; time is confounded with device, provider, applications and network.

## Immediate collection gate

The original October 19 feasibility cutoff has passed. Revised dates are:

- October 29: one paired direct/VPN pilot, extractor/provenance review and instructor
  agreement on the reduced temporal study.
- November 2: decide whether compatible real data is feasible and freeze the main
  historical experiments. Do not invent a temporal result if compatibility fails.
- November 9: finish the small modern evaluation if feasible.
- November 16: complete report draft including temporal results or explicit limits.
- November 30: finish final reproducibility check and presentation.
- December 5: submit.

The collection protocol remains in `modern_collection_protocol.md`; its past
cutoffs are historical planning context, superseded by the dates above.
