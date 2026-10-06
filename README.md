# network-fingerprinting-project

This repository contains the modeling and evaluation pipeline for the VPN/Tor traffic classification project.

## Data storage

Do not commit raw datasets or large generated outputs into the repository. Download them into the local data folders under `data/` and keep them out of version control via the project `.gitignore`.

Recommended layout:

```text
project-root/
├── .gitignore
├── requirements.txt
├── run_baseline.py
├── src/
├── tests/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
└── .venv/
```

### Raw dataset location

Place downloaded datasets in:

```text
project-root/data/raw/
```

For example:

- `data/raw/ISCXVPN2016/`
- `data/raw/ISCXTor2016/`

The project code expects data to be loaded from this local directory rather than from repository-tracked files.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python run_baseline.py data/raw/your_dataset.csv --output data/processed/baseline_metrics.json
```

## Generalization experiments

```bash
.venv/bin/python run_generalization.py 'data/raw/Scenario B-ARFF.zip' --timeout 15
```

This runs a stratified random baseline and seven leave-one-application-category-out
experiments with the same logistic-regression pipeline. Each fold trains on the
other six categories and tests on both VPN and Non-VPN flows from the held-out
category. Results include accuracy, macro-F1, macro-precision, macro-recall,
class counts, predictions, and confusion matrices (rows=true, columns=predicted;
0=Non-VPN, 1=VPN). JSON and CSV outputs go to `data/processed/generalization/`.
Only one timeout variant is loaded: other timeout files and AllinOne files must
not be concatenated as independent observations.

The model uses the native numeric flow features, excluding labels and identifying
metadata. Missing/infinite values are imputed using training medians; scaling is
also fitted on training only. Earlier feature construction incorrectly treated
interarrival-time sums as packet counts and flow byte rates as directional byte
counts; experiments now avoid these derived aliases. Prior metrics from the old
feature pipeline should be rerun before comparison.

Session-disjoint evaluation requires genuine, non-null `capture_session` IDs.
The local ARFF exports contain none, so their session-disjoint evaluation is
unavailable. Source files, application categories, and row numbers are not
substitutes for capture sessions. Recover flow-to-capture provenance from original
captures before claiming this milestone complete.

See `reports/progress_2026-10-05.md` for measured results and remaining work.

## Tor CSVs

`load_tor_dataset('data/raw/Scenario-A-merged_5s.csv')` loads the binary
Tor/NonTor CSV, trims column whitespace, removes exact duplicate rows, and
excludes IPs and ports. Pass its result to `run_baseline_experiment`.
Scenario B has application-only labels and is rejected by this binary loader.
See `reports/tor_inspection_2026-10-05.md` for the initial baseline and limitations.

## Repeated two-model study

```bash
.venv/bin/python run_repeated_study.py 'data/raw/Scenario B-ARFF.zip'
.venv/bin/python plot_study.py
```

This study removes exact duplicates and runs logistic regression and Random Forest
on five random baseline splits and five stratified training bootstraps per LOAO
category (seeds 42–46). It also saves full-training LOAO controls at seed 42.
LOAO test flows remain fixed and excluded from every resample. Reported standard
deviations describe run sensitivity, not session-level confidence intervals.
Compact metrics, CSVs, PNG/PDF figures and full-training controls are under
`reports/vpn_study/`; large prediction arrays are under `data/processed/vpn_study/`.
See `reports/vpn_study/findings.md`, `reports/dataset_compatibility.md`, and
`reports/modern_collection_protocol.md` for analysis and the remaining schedule.

For a plain-language guide to every result format and the study terminology,
start with [the report index](reports/README.md).
