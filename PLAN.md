# PLAN.md — VPN/Tor Traffic Generalization Project

## 1. Project Goal

Build a reproducible machine-learning system that classifies network traffic as **Normal**, **VPN**, or **Tor** using flow-level metadata. The main research focus is **generalization**, not only benchmark accuracy.

The project evaluates:

1. **Baseline classification** — train/test on historical traffic.
2. **Leave-One-Application-Out (LOAO)** — train without one application category and test on that unseen category.
3. **Temporal generalization** — train on older traffic and test on newer traffic.
4. **Combined generalization** — test traffic that differs in both application category and time period.

This project is scoped for **one student in one college semester**.

## 2. Research Questions

- **RQ1:** How accurately can Normal, VPN, and Tor traffic be classified using encrypted flow metadata?
- **RQ2:** Can the classifier generalize to an application category that was completely excluded from training?
- **RQ3:** Does a model trained on historical traffic remain accurate on newer traffic?
- **RQ4:** How much does performance change when both application type and time period differ from training?

## 3. Datasets

### Required historical datasets

**ISCXVPN2016**  
Primary source for Normal and VPN traffic with application labels.  
https://www.unb.ca/cic/datasets/vpn.html

**ISCXTor2016**  
Primary source for Normal and Tor traffic with application labels.  
https://www.unb.ca/cic/datasets/tor.html

Expected application categories include browsing, chat, streaming, VoIP, file transfer, P2P, and email.

### Optional reference dataset

**CIC-Darknet2020**  
Useful for comparison or supplementary experiments, but not as an independent generalization dataset because it is derived from earlier VPN/Tor datasets.  
https://www.unb.ca/cic/datasets/darknet2020.html

### Modern evaluation data

Collect or obtain a small modern dataset for temporal testing.

Preferred classes:
- Normal
- OpenVPN
- Tor

Preferred application categories:
- Browsing
- Streaming
- File transfer
- Chat

Optional stretch class:
- WireGuard

WireGuard is not required for the minimum viable project.

## 4. Methodology Rules

### Avoid information leakage

Do **not** use these as predictive features:
- Source/destination IP
- Hostnames or DNS names
- MAC addresses
- Capture filenames
- Application labels
- VPN/Tor labels
- Unique capture identifiers
- Ports if they trivially identify a class or application

The model should learn traffic behavior rather than identifiers.

### Preferred features

Use flow-level metadata such as:
- Flow duration
- Forward/backward packet counts
- Forward/backward bytes
- Total bytes
- Mean/median/std/min/max packet size
- Mean/std inter-arrival time
- Packets per second
- Bytes per second
- Forward/backward packet ratio
- Forward/backward byte ratio

### Splitting rules

Do not use a random row-level split as the main experiment. Random splitting may be used only as a baseline.

Primary evaluation should separate data by:
- Application category
- Capture/session
- Time period

## 5. Labeling Strategy

Normalize datasets into:

### Traffic class

```text
normal
vpn
tor
```

### Application category

```text
browsing
chat
streaming
voip
file_transfer
p2p
email
```

Recommended canonical schema:

```text
sample_id
dataset
capture_id
time_period
traffic_class
application
<feature columns...>
```

## 6. Repository Structure

```text
project-root/
├── PLAN.md
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   ├── datasets.yaml
│   └── experiments.yaml
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── README.md
├── src/
│   ├── data/
│   │   ├── load_vpn2016.py
│   │   ├── load_tor2016.py
│   │   ├── normalize_labels.py
│   │   └── validate_dataset.py
│   ├── features/
│   │   ├── build_features.py
│   │   └── feature_sets.py
│   ├── models/
│   │   ├── train_logistic.py
│   │   ├── train_random_forest.py
│   │   └── train_xgboost.py
│   ├── experiments/
│   │   ├── baseline.py
│   │   ├── leave_one_application_out.py
│   │   ├── temporal_generalization.py
│   │   └── combined_generalization.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── plots.py
│   │   └── summarize.py
│   └── utils/
│       ├── paths.py
│       ├── seed.py
│       └── logging.py
├── scripts/
│   ├── prepare_data.py
│   ├── run_baseline.py
│   ├── run_loao.py
│   ├── run_temporal.py
│   └── run_all.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── results/
│   ├── metrics/
│   ├── figures/
│   └── models/
└── tests/
    ├── test_labels.py
    ├── test_features.py
    └── test_splits.py
```

The structure may be simplified if necessary, but keep data loading, feature creation, experiments, and evaluation separated.

## 7. Models

### Required
1. Logistic Regression
2. Random Forest

### Recommended
3. XGBoost or LightGBM

### Stretch only
- 1D CNN
- LSTM
- Other sequence models

Do not prioritize deep learning until the classical pipeline is complete.

## 8. Evaluation Metrics

Report:
- Accuracy
- Macro precision
- Macro recall
- Macro F1
- Per-class precision/recall/F1
- Confusion matrix

Treat **Macro F1** as the primary summary metric.

Also calculate:

```text
generalization_drop = baseline_macro_f1 - shifted_macro_f1
```

## 9. Experiments

### Experiment A — Baseline

Train on historical data and test on held-out historical traffic. Split by session/capture where possible.

Output:
- Accuracy
- Macro F1
- Per-class metrics
- Confusion matrix

### Experiment B — Leave-One-Application-Out

For each application `X`:

```text
train = all historical samples where application != X
test  = all historical samples where application == X
```

Target remains:

```text
normal / vpn / tor
```

Repeat for every application with enough samples.

Output:
- Macro F1 by held-out application
- Per-class metrics
- Comparison against baseline

### Experiment C — Temporal Generalization

```text
Train: historical traffic
Test:  modern traffic
```

Use the same feature definitions and labels.

Output:
- Macro F1
- Per-class metrics
- Confusion matrix
- Drop relative to historical baseline

### Experiment D — Combined Shift

Where possible:

```text
Train: historical traffic excluding application X
Test:  modern traffic from application X
```

This is the strongest generalization test.

## 10. Modern Traffic Collection

Minimum application set:

```text
browsing
streaming
file_transfer
chat
```

For each application, collect:

```text
normal
openvpn
tor
```

Capture multiple independent sessions rather than one long capture.

Track metadata such as:

```text
capture_id
date
application
traffic_class
os
browser_or_client
vpn_client
notes
```

Do not commit credentials or sensitive payload data.

Do not commit large raw PCAPs to Git. Keep them outside Git and document expected paths.

## 11. Development Phases

### Phase 1 — Repository Setup
- [ ] Create Python virtual environment
- [ ] Add `requirements.txt`
- [ ] Add `.gitignore`
- [ ] Create directories
- [ ] Add config files
- [ ] Add reproducible seed handling

Suggested setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy scikit-learn matplotlib pyyaml joblib
```

Optional later:

```bash
pip install xgboost
```

### Phase 2 — Historical Data Pipeline
- [ ] Load ISCXVPN2016
- [ ] Load ISCXTor2016
- [ ] Normalize labels
- [ ] Remove leakage-prone fields
- [ ] Validate missing values and class counts
- [ ] Save processed dataset

**Acceptance criterion:** one processed table exists with traffic class, application, capture/session identifier, and approved model features.

### Phase 3 — Baseline Models
- [ ] Logistic Regression
- [ ] Random Forest
- [ ] Optional XGBoost
- [ ] Shared evaluation functions
- [ ] Confusion matrices
- [ ] Save metrics to JSON/CSV

**Acceptance criterion:** one command can train and evaluate a baseline model.

Example:

```bash
python scripts/run_baseline.py
```

### Phase 4 — LOAO
- [ ] Implement reusable LOAO splitter
- [ ] Verify held-out application is absent from training
- [ ] Run all valid application holdouts
- [ ] Aggregate metrics

Expected result file:

```text
results/metrics/loao_results.csv
```

### Phase 5 — Modern Dataset
- [ ] Define collection procedure
- [ ] Collect/obtain Normal traffic
- [ ] Collect/obtain VPN traffic
- [ ] Collect/obtain Tor traffic
- [ ] Run the same feature pipeline
- [ ] Validate schema compatibility

### Phase 6 — Temporal Evaluation
- [ ] Train on historical data
- [ ] Test on modern data
- [ ] Record generalization drop
- [ ] Generate confusion matrix
- [ ] Analyze class-specific changes

### Phase 7 — Combined Generalization
- [ ] Select comparable application categories
- [ ] Remove application X from historical training
- [ ] Test on modern application X
- [ ] Repeat where valid

### Phase 8 — Final Analysis
- [ ] Baseline comparison table
- [ ] LOAO table
- [ ] Temporal table
- [ ] Combined-shift table
- [ ] Confusion matrices
- [ ] Generalization-drop figure
- [ ] Final README
- [ ] Reproducibility check

## 12. Mid-Semester Milestone

By mid-semester:
- Historical datasets acquired
- Preprocessing working
- Labels normalized
- Feature pipeline complete
- Leakage-prone features removed
- Logistic Regression working
- Random Forest working
- Baseline evaluation complete
- At least one LOAO experiment complete
- Modern-data collection procedure defined

A good demo is:

```text
Historical data
      ↓
Preprocessing
      ↓
Feature extraction
      ↓
Model training
      ↓
Normal / VPN / Tor predictions
      ↓
Baseline + LOAO comparison
```

## 13. Final Deliverables

### Code artifact

A reproducible Python repository capable of:

```text
prepare data
→ train models
→ run experiments
→ generate metrics
→ generate plots
```

### Required evaluation

1. Historical baseline
2. Leave-One-Application-Out
3. Temporal generalization
4. Combined shift where feasible

### README requirements

Document:
- Project purpose
- Environment setup
- Dataset requirements
- Expected dataset locations
- Preprocessing
- How to run experiments
- How to reproduce results
- Known limitations

## 14. Main Risks and Fallbacks

### Modern traffic is difficult to collect
Fallback: use a compatible newer public dataset. Baseline + LOAO + cross-dataset testing can still produce a complete project.

### Dataset schemas differ
Fallback: use a smaller shared feature subset available across both datasets.

### Class imbalance
Mitigation: use macro F1, class weights where appropriate, and per-class metrics.

### Dataset leakage
Mitigation: remove identifiers, split by capture/session, validate split membership, and add leakage tests.

### Deep learning takes too long
Fallback: skip it. Logistic Regression, Random Forest, and XGBoost are sufficient.

## 15. Tests Local Agents Should Implement

### Label tests
Ensure only these traffic labels appear:

```text
normal
vpn
tor
```

### Leakage tests
Fail if forbidden columns enter the model feature list.

### LOAO tests

For held-out application `X`:

```python
assert X not in train["application"].unique()
assert set(test["application"].unique()) == {X}
```

### Temporal tests
Ensure historical training data contains no modern captures.

### Schema tests
Historical and modern datasets must expose compatible model feature columns.

## 16. Rules for Local Coding Agents

1. Read `PLAN.md` before making architectural changes.
2. Prefer small, testable changes.
3. Do not silently change the research question.
4. Do not introduce payload inspection.
5. Do not add leakage-prone identifiers as features.
6. Do not make random row-level splits the primary evaluation.
7. Use fixed seeds for reproducibility.
8. Save experiment configuration with results.
9. Do not commit large raw PCAPs.
10. Keep raw, processed, and result data separate.
11. Add tests for preprocessing and dataset splitting logic.
12. Update `README.md` when user-facing commands change.
13. Prefer config files over absolute paths.
14. Keep macOS compatibility in mind for local development in VS Code.
15. Treat deep learning and WireGuard as stretch goals.

## 17. Suggested Initial Agent Tasks

Work in this order:

1. Create the repository structure.
2. Create `requirements.txt`, `.gitignore`, `config/datasets.yaml`, `config/experiments.yaml`, and `data/README.md`.
3. Implement the normalized dataset schema and label mapping.
4. Implement historical dataset loaders.
5. Implement validation and leakage checks.
6. Implement the baseline Random Forest pipeline.
7. Implement shared evaluation utilities.
8. Implement LOAO splitting and experiments.
9. Only then begin modern traffic collection and temporal-generalization work.

## 18. Definition of Minimum Viable Success

The project is successful if the repository can reproducibly answer:

```text
1. How well does Normal/VPN/Tor classification work on historical data?
2. How much does performance change when the application is unseen?
3. How much does performance change when the traffic is temporally newer?
4. How much does performance change when both shifts occur together?
```

A specific accuracy threshold is **not** required. A significant performance drop is still a valid research result.

The primary goal is to measure and explain **generalization behavior**, not to maximize benchmark accuracy.
