# VPN/Tor Traffic Classification — Condensed Semester Project Plan

## 1. Working Title

**Beyond Random Splits: Evaluating Temporal and Application Generalization in VPN and Tor Traffic Classification**

## 2. Project Goal

Build a network-traffic classifier that predicts whether an encrypted flow is:

- **Normal / Direct**
- **VPN**
- **Tor**

The main contribution is **not** simply achieving high classification accuracy. The project tests whether learned VPN/Tor fingerprints remain useful when:

1. the underlying **application category was unseen during training** (leave-one-application-out generalization), and
2. the traffic comes from a **different time period / modern environment** (temporal generalization).

### Core research question

> Do VPN/Tor classifiers learn durable tunnel/protocol characteristics, or do they mostly learn application- and dataset-specific artifacts?

---

## 3. Research Questions / Hypotheses

### RQ1 — Baseline
How accurately can Normal, VPN, and Tor traffic be classified using encrypted flow metadata under a conventional within-dataset split?

### RQ2 — Application Generalization
How well does the classifier perform when the test traffic belongs to an application category that was completely excluded from training?

### RQ3 — Temporal Generalization
How well does a classifier trained on historical VPN/Tor traffic perform on traffic captured in a modern environment?

### RQ4 — Combined Shift
How well does the classifier perform when **both** the application category and capture period differ from the training data?

### Expected hypotheses

- **H1:** Random/within-dataset performance will be substantially higher than leave-one-application-out performance.
- **H2:** Historical → modern performance will degrade relative to historical → historical performance.
- **H3:** Combined temporal + application shift will cause the largest degradation.

---

## 4. Required Datasets

### A. ISCXVPN2016 — Primary Historical VPN Dataset

This project builds on the prior work that showed encrypted traffic can be distinguished using time-related flow statistics, particularly for Tor traffic and VPN traffic characterization [1, 2].

**Use for:** Normal vs VPN training/evaluation and application labels.

Official page: <https://www.unb.ca/cic/datasets/vpn.html>

Properties:

- Contains regular and VPN sessions.
- VPN traffic was generated using OpenVPN.
- Includes multiple traffic/application categories such as browsing, email, chat, streaming, file transfer, VoIP, and P2P.
- Raw PCAP and flow-level data are available.

**Role in project:** historical Normal + VPN source.

### B. ISCXTor2016 — Primary Historical Tor Dataset

**Use for:** Tor examples and matched application-category evaluation.

Official page: <https://www.unb.ca/cic/datasets/tor.html>

Properties:

- Contains Tor and non-Tor traffic.
- Categories include browsing, email, chat, audio/video streaming, file transfer, VoIP, and P2P.
- Raw PCAP and flow-level CSV data are available.
- The non-Tor portion reuses benign traffic from the VPN project.

**Important:** Do **not** blindly concatenate all non-Tor traffic with ISCXVPN2016 normal traffic; this can duplicate observations. Use one canonical source for historical Normal traffic or explicitly deduplicate.

### C. Self-Collected Modern Dataset — Required for Temporal Generalization

Collect a small but controlled modern dataset during the semester.

Target classes:

- Normal
- OpenVPN
- Tor

Target application categories (minimum 3–4):

- Web browsing
- Video/audio streaming
- File transfer/download
- Chat or another interactive application

Recommended collection strategy:

- Repeat each **class × application** combination across multiple independent sessions.
- Prefer at least **10–20 sessions per combination** if practical.
- Keep sessions separately identifiable so train/test splits can be made by session rather than individual flow.
- Record date, OS, browser/application version, VPN/Tor configuration, capture interface, and network environment.

Example minimum collection grid:

| Application | Normal | OpenVPN | Tor |
|---|---:|---:|---:|
| Browsing | 15 sessions | 15 | 15 |
| Streaming | 15 | 15 | 15 |
| File transfer | 15 | 15 | 15 |
| Chat/interactive | 15 | 15 | 15 |

This is **180 sessions** at 15 repetitions per cell. Reduce repetitions if capture time becomes a bottleneck; consistency and session independence are more important than raw size.

### D. CIC-Darknet2020 — Optional Convenience / Sanity Dataset

Official page: <https://www.unb.ca/cic/datasets/darknet2020.html>

CIC-Darknet2020 combines ISCXVPN2016 and ISCXTor2016. It may be useful for prototyping or comparison, but it should **not** be treated as an independent cross-dataset test set because it is derived from the same underlying historical datasets.

### E. 2026 WireGuard Dataset — Optional Stretch Dataset

Paper/data description: <https://pmc.ncbi.nlm.nih.gov/articles/PMC13049606/>

Useful properties:

- Collected in December 2025 and published in 2026.
- ~80 hours of residential traffic from 10 devices.
- 226,454 flows.
- Contains encrypted-side flow features and first-255-packet sequences.
- Designed to support cross-session and early-flow classification.

**Potential use:** add a modern VPN protocol / external modern dataset experiment. Keep this a stretch goal because the primary project is Normal/OpenVPN/Tor generalization.

### References

[1] Arash Habibi Lashkari, Gerard Draper-Gil, Mohammad Saiful Islam Mamun and Ali A. Ghorbani, "Characterization of Tor Traffic Using Time Based Features," In the proceeding of the 3rd International Conference on Information System Security and Privacy, SCITEPRESS, Porto, Portugal, 2017.

[2] Gerard Drapper Gil, Arash Habibi Lashkari, Mohammad Mamun, Ali A. Ghorbani, "Characterization of Encrypted and VPN Traffic Using Time-Related Features," In Proceedings of the 2nd International Conference on Information Systems Security and Privacy (ICISSP 2016), pages 407-414, Rome, Italy.

---

## 5. Target Labels

### Primary classification target

```text
0 = Normal
1 = VPN
2 = Tor
```

### Auxiliary metadata retained for splitting/evaluation

Every sample should also retain:

- `application_category`
- `application_name` if available
- `dataset_source`
- `capture_year`
- `capture_session`
- `traffic_class` (Normal/VPN/Tor)

Do **not** use the auxiliary identifiers as classifier input features.

---

## 6. Preprocessing Strategy

### Preferred unit: bidirectional network flow

For every flow, extract payload-independent metadata.

Candidate features:

- Flow duration
- Forward packet count
- Backward packet count
- Forward byte count
- Backward byte count
- Mean/median/std/min/max packet size
- Forward/backward packet-size statistics
- Mean/std/min/max inter-arrival time
- Packets per second
- Bytes per second
- Forward/backward packet ratio
- Forward/backward byte ratio
- TCP flag statistics where appropriate
- Burst-related statistics if easily available

### Exclude leakage-prone features from model input

Do **not** train on:

- Source/destination IP address
- Known Tor relay IP lists
- Domain names / DNS answers
- TLS SNI / hostnames
- Application labels
- Capture filename/session ID
- Absolute timestamp/date
- Payload contents
- Features that trivially identify a known endpoint

Ports should preferably be excluded from the main model or tested separately as an ablation, because they can become shortcuts.

### Tooling

Recommended stack:

- Python
- pandas / NumPy
- scikit-learn
- XGBoost or LightGBM
- matplotlib
- Wireshark / tcpdump for modern capture
- CICFlowMeter, NFStream, Zeek, or a consistent custom flow-extraction pipeline

**Important:** Ideally process historical and modern PCAPs through the **same feature extraction pipeline**. Using different feature extractors for old and modern traffic can create artificial dataset differences.

---

## 7. Dataset Harmonization

Historical VPN and Tor datasets must be mapped into a common schema.

Example application-category mapping:

```text
Browsing        -> browsing
AudioStreaming  -> streaming
VideoStreaming  -> streaming
Chat            -> chat
Email           -> email
FileTransfer    -> file_transfer
FTP             -> file_transfer
VoIP            -> voip
P2P             -> p2p
```

Only use application categories that can be mapped reliably across the relevant datasets.

For the strongest leave-one-out experiment, prioritize common categories such as:

- browsing
- streaming
- file transfer
- chat
- VoIP (if modern collection is feasible)

---

## 8. Experimental Design

### Experiment 0 — Sanity / Random Baseline

Train and test using a stratified split within historical data.

Purpose: establish an optimistic conventional benchmark.

**Do not make this the primary result.**

### Experiment 1 — Session-Disjoint Historical Baseline

Train and test on historical data while ensuring traffic from the same capture/session cannot appear in both sets.

This gives a more credible baseline than a random per-flow split.

### Experiment 2 — Leave-One-Application-Out (LOAO)

For each application category `A`:

```text
TRAIN = all historical application categories except A
TEST  = historical category A only
TARGET = Normal / VPN / Tor
```

Repeat for every feasible application category.

Example:

```text
Train: browsing + chat + file_transfer + voip
Test:  streaming
```

This tests whether the model recognizes tunneling behavior rather than memorizing application behavior.

### Experiment 3 — Temporal Generalization

```text
TRAIN = historical ISCXVPN2016 + ISCXTor2016
TEST  = self-collected modern traffic
```

Use only compatible features and labels.

Report the drop relative to historical/session-disjoint performance.

### Experiment 4 — Temporal + Application Generalization

Strongest experiment.

For application category `A`:

```text
TRAIN = historical data excluding application A
TEST  = modern application A
```

This introduces both:

- an unseen application condition, and
- a large temporal/environment shift.

Repeat for every modern application category that can be mapped to the historical taxonomy.

### Optional Experiment 5 — Limited Modern Adaptation

If historical → modern performance drops substantially, retrain/fine-tune using increasing fractions of labeled modern data:

```text
0% / 1% / 5% / 10% / 25%
```

Question:

> How much recent labeled traffic is required to recover useful performance?

---

## 9. Models

Keep model complexity secondary to experimental rigor.

### Required baselines

1. **Logistic Regression** — simple linear baseline
2. **Random Forest** — robust nonlinear baseline + feature importance
3. **XGBoost or LightGBM** — strong tabular classifier

### Optional

- 1D CNN or LSTM using packet-size/direction/timing sequences

Only add deep learning after the full classical-ML experiment pipeline works.

---

## 10. Evaluation Metrics

Primary metric:

- **Macro F1** — important because classes may be imbalanced.

Also report:

- Accuracy
- Per-class precision
- Per-class recall
- Per-class F1
- Confusion matrix
- Balanced accuracy

Optional:

- One-vs-rest ROC-AUC / PR-AUC
- Confidence intervals via bootstrap or repeated runs

### Most important comparisons

Report performance drops, not just absolute scores:

```text
Generalization Drop = Baseline Macro-F1 - Generalization Macro-F1
```

Example final table:

| Test condition | Macro-F1 | Δ from baseline |
|---|---:|---:|
| Random split | — | — |
| Session-disjoint | — | — |
| LOAO | — | — |
| Historical → modern | — | — |
| LOAO + historical → modern | — | — |

---

## 11. Data Leakage Controls — Critical

These rules are essential to making the results defensible.

1. **Never split individual flows randomly if multiple flows originate from the same capture/session** for the primary experiments.
2. Keep capture/session groups intact when splitting.
3. Remove IP addresses and endpoint identifiers from model inputs.
4. Do not allow duplicates from the VPN and Tor datasets' shared normal traffic to appear across train/test sets.
5. Fit normalization, feature selection, imputation, and dimensionality reduction **only on training data**.
6. Do not tune hyperparameters on the final modern test set.
7. Keep the modern temporal test set untouched until the historical pipeline is finalized when practical.
8. Record all preprocessing decisions and random seeds.

---

## 12. Modern Data Collection Strategy

### Capture setup

Use the same machine/VM setup where practical for all three routing modes:

```text
Application activity
        |
        +-- Direct connection  -> Normal capture
        +-- OpenVPN tunnel     -> VPN capture
        +-- Tor                -> Tor capture
```

Capture traffic with Wireshark/tcpdump at a location where the classifier sees the encrypted/tunneled traffic rather than decrypted inner traffic.

### Session protocol

For every run:

1. Start clean capture.
2. Start routing mode.
3. Perform a predefined activity for a fixed or bounded period.
4. Stop activity.
5. Stop capture.
6. Save metadata/label.
7. Reset connections where feasible.
8. Repeat.

Avoid collecting every sample in one continuous capture; independent sessions are much more valuable for generalization testing.

### Suggested reproducible tasks

- **Browsing:** visit a fixed list of ordinary websites / pages.
- **Streaming:** play selected video/audio clips for a fixed interval.
- **File transfer:** download files from controlled/test sources.
- **Chat/interactive:** use a reproducible interactive web/app workflow.

Document the exact procedure so it can be repeated.

---

## 13. Repository / Folder Structure

```text
project/
├── README.md
├── requirements.txt
├── config/
│   └── experiments.yaml
├── data/
│   ├── raw/
│   │   ├── iscxvpn2016/
│   │   ├── iscxtor2016/
│   │   └── modern/
│   ├── interim/
│   └── processed/
├── metadata/
│   └── modern_capture_log.csv
├── src/
│   ├── preprocessing/
│   ├── features/
│   ├── models/
│   └── evaluation/
├── experiments/
│   ├── baseline.py
│   ├── leave_one_app_out.py
│   └── temporal.py
├── results/
│   ├── metrics/
│   ├── figures/
│   └── models/
└── notebooks/
    └── exploratory_analysis.ipynb
```

Keep reusable pipeline logic in `src/`; notebooks should mainly be used for exploration/visualization.

---

## 14. Suggested Semester Timeline (14–15 Weeks)

### Weeks 1–2 — Research + Environment

- Finalize research questions.
- Download datasets.
- Read dataset papers/documentation.
- Define label/category mappings.
- Build repository and reproducible environment.

### Weeks 3–4 — Preprocessing

- Parse historical data.
- Standardize feature schema.
- Remove leakage-prone fields.
- Create session/application metadata.
- Perform exploratory analysis.

### Weeks 5–6 — Baselines

- Train Logistic Regression, Random Forest, XGBoost/LightGBM.
- Establish random and session-disjoint baselines.
- Create reproducible evaluation scripts.

### Weeks 7–8 — Leave-One-Application-Out

- Implement grouped application splits.
- Run all LOAO experiments.
- Analyze application-specific degradation.

### Weeks 8–10 — Modern Capture

- Finalize capture protocol.
- Collect Normal/OpenVPN/Tor traffic.
- Validate labels/captures as data is collected.
- Process using the same feature pipeline.

**Start collection before the historical experiments are completely finished; do not leave all data collection until the end.**

### Weeks 10–11 — Temporal Evaluation

- Historical → modern testing.
- Combined temporal + LOAO testing.
- Diagnose distribution shift.

### Weeks 12–13 — Analysis / Stretch Work

- Feature importance or SHAP.
- Optional limited-modern-data adaptation.
- Optional WireGuard experiment.
- Statistical checks / repeated runs.

### Weeks 14–15 — Final Deliverables

- Final figures/tables.
- Write report.
- Build presentation/demo.
- Re-run experiments from clean environment to verify reproducibility.

---

## 15. Minimum Viable Project (MVP)

The project is complete and defensible if the following are finished:

- [ ] ISCXVPN2016 processed
- [ ] ISCXTor2016 processed
- [ ] Normal/VPN/Tor labels harmonized
- [ ] Leakage-prone fields removed
- [ ] Session-disjoint baseline
- [ ] At least 2 classical ML models
- [ ] Leave-one-application-out evaluation
- [ ] Small controlled modern Normal/OpenVPN/Tor dataset
- [ ] Historical → modern evaluation
- [ ] Macro-F1 + per-class metrics + confusion matrices
- [ ] Comparison of baseline vs application shift vs temporal shift
- [ ] Reproducible code/configuration

Anything beyond this is a stretch goal.

---

## 16. Stretch Goals — Priority Order

1. **Limited modern-data adaptation** — 1/5/10/25% modern labels.
2. **Feature importance / SHAP** — identify which metadata signals remain stable or drift.
3. **WireGuard** — test a modern VPN protocol using self-capture or the 2026 dataset.
4. **Early-flow classification** — first 5/10/20/50 packets.
5. **Sequence model** — 1D CNN/LSTM.

Avoid adding stretch goals until the MVP generalization experiments are working.

---

## 17. Main Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Historical and modern feature schemas differ | Reprocess PCAPs with one common extractor where possible |
| Duplicate Normal traffic across UNB datasets | Use one canonical Normal source / deduplicate |
| Random split inflates results | Use grouped session/application splits |
| Model learns IP/port shortcuts | Remove endpoint IDs; ablate ports |
| Modern dataset too small | Prioritize repeated independent sessions over many applications |
| Class imbalance | Macro-F1, balanced sampling/class weights |
| Modern apps do not match historical categories | Select 3–4 categories with clear semantic mapping |
| Tor traffic collection behaves differently than historical Tor | Treat this as part of temporal/environment shift and document setup |
| Too much time spent on deep learning | Finish RF/XGBoost experiments first |
| Temporal results confounded by different extractor | Use identical extraction pipeline whenever possible |

---

## 18. Expected Final Figures / Tables

Plan the project so it produces these artifacts:

1. Dataset/class/application distribution table.
2. Baseline Normal/VPN/Tor confusion matrix.
3. LOAO macro-F1 by held-out application.
4. Historical vs modern performance comparison.
5. Combined temporal + application-shift comparison.
6. Per-class Normal/VPN/Tor recall under each evaluation condition.
7. Optional feature-importance comparison between historical and modern traffic.
8. Optional learning curve showing performance after adding small amounts of modern labeled data.

The central visualization should show the **performance degradation as evaluation becomes more realistic**:

```text
Random Split
    -> Session-Disjoint
        -> Unseen Application
            -> Modern Traffic
                -> Modern + Unseen Application
```

---

## 19. Success Criteria

The project is successful even if cross-domain accuracy is poor.

A valuable result could be either:

- the classifier generalizes well, providing evidence that VPN/Tor traffic has durable observable fingerprints, **or**
- performance collapses under temporal/application shift, providing evidence that conventional benchmark results overestimate real-world generalization.

The important requirement is that the evaluation cleanly isolates and measures the shifts.

---

## 20. Immediate Next Steps

1. Download ISCXVPN2016 and ISCXTor2016 flow data and inspect their exact schemas.
2. Determine whether raw PCAP reprocessing is necessary for a common historical/modern feature pipeline.
3. Create the canonical label mapping: `Normal`, `VPN`, `Tor` + application categories.
4. Identify capture/session grouping fields before doing any train/test split.
5. Implement a minimal preprocessing pipeline and Random Forest baseline.
6. Implement one LOAO split (e.g. hold out streaming) as proof of concept.
7. Design and test a **small pilot modern capture** for one application under Normal/OpenVPN/Tor before committing to full collection.
8. Once the pilot passes through the same feature pipeline, scale modern collection.

---

## 21. Primary Sources

- UNB CIC — ISCXVPN2016: <https://www.unb.ca/cic/datasets/vpn.html>
- UNB CIC — ISCXTor2016: <https://www.unb.ca/cic/datasets/tor.html>
- UNB CIC — CIC-Darknet2020: <https://www.unb.ca/cic/datasets/darknet2020.html>
- UNB CIC dataset index: <https://www.unb.ca/cic/datasets/>
- Sajid et al. (2026), WireGuard flow-level dataset: <https://pmc.ncbi.nlm.nih.gov/articles/PMC13049606/>

---

## One-Sentence Project Pitch

> **This project evaluates whether encrypted-traffic classifiers can reliably distinguish Normal, VPN, and Tor traffic when tested on both unseen application categories and traffic collected roughly a decade after the training datasets, exposing whether benchmark accuracy reflects durable protocol fingerprints or dataset-specific shortcuts.**
