# Beyond Random Splits: Application Generalization in VPN Traffic Classification

**Author:** [Your Name]  
**Status:** Research report draft, October 26, 2026  
**Broader project:** Generalization in VPN/Tor Network Traffic Classification

## Abstract

This project examines whether high within-dataset classification scores predict
performance on unseen application categories. Historical ISCXVPN2016 flow exports
support seven VPN/direct category holdouts. Logistic regression and Random Forest
are evaluated using random splits, exact-feature-vector group splits, and a
matched comparison that tests category-seen and category-unseen models on the
same flows with equal training row counts. After exact deduplication, 18,074 VPN
flows remain. Across seven categories and five splits per category, Random
Forest's mean macro-F1 is 0.902 with the category represented in training and
0.535 with the category excluded. Its largest average drop is 0.606 for VoIP.
Separate Tor/NonTor baselines use 83,701 deduplicated flows and achieve high
within-dataset scores, but cannot establish application or temporal transfer.
These results support an application-generalization gap for the VPN model under
the evaluated design. Genuine session metadata and compatible modern traffic
remain unavailable, so temporal and combined shifts are not yet empirically
answered.

## 1. Motivation and research questions

Traffic classification from timing and rate statistics can be useful even when
payloads are encrypted. A model can nevertheless exploit patterns specific to
particular workloads or collection conditions. A random flow split can retain
those patterns in both training and testing, producing an optimistic estimate of
performance on a new environment.

The original project asks four questions: historical classification performance,
unseen-application generalization, historical-to-modern transfer, and the joint
application/time shift. This draft answers the historical questions only where
the available labels permit them. VPN and Tor are treated as separate binary
tasks. A pooled normal/VPN/Tor classifier remains unresolved because source
features, collection settings, and benign-traffic overlap have not been reconciled.
This separation is a documented limitation of the original scope, not evidence
that the three-class question has been completed.

## 2. Data and provenance

### 2.1 VPN data

The local Scenario B archive contains transport and application labels. The
15-second filename variant includes browsing, chat, email, file transfer, P2P,
streaming, and VoIP in VPN/direct forms. The official dataset description identifies
OpenVPN UDP and describes controlled application workloads and ISCXFlowMeter
exports. Other timeout variants are not concatenated as independent observations.
[ISCXVPN2016 dataset description](https://www.unb.ca/cic/datasets/vpn.html).

The selected member contains 18,758 rows. Removing 684 exact duplicate rows leaves
18,074: 9,380 VPN and 8,694 direct flows. There are 59 remaining repeated numeric
feature vectors, including 23 unique vectors associated with conflicting transport
labels. Such vectors can arise from coarse features; they are not assumed to
identify a real capture session. No genuine capture/session ID is supplied by the
export.

### 2.2 Tor data

The binary Scenario A CSV contains 84,194 rows. Removing 493 exact duplicates
leaves 83,701: 14,478 Tor and 69,223 NonTor. Its 24 native numeric features include
protocol, duration, rates, interarrival statistics, active statistics and idle
statistics. Twelve numeric cells are missing after nonfinite values are converted
to missing values. Median imputation is fitted on training only.

All 14,508 application-labeled rows in the local Tor Scenario B file match Tor rows
in Scenario A when endpoints and numeric features are joined exactly. Thus these
files overlap; concatenating them would duplicate observations. Application labels
for NonTor flows are unavailable. The official description also states that
NonTor traffic reuses benign traffic from the VPN project, creating a further
cross-dataset overlap risk. [ISCXTor2016 dataset description](https://www.unb.ca/cic/datasets/tor.html).

CIC-Darknet2020 combines those older sources and is not an independent modern
traffic collection. [CIC-Darknet2020 dataset description](https://www.unb.ca/cic/datasets/darknet2020.html).

## 3. Methods

### 3.1 Features and models

The VPN study uses 23 native numeric time/rate columns. Source/destination IPs,
ports, target labels, application metadata, capture identifiers, years, and dataset
identifiers are excluded. The experiments do not fabricate directional byte or
packet counts from interarrival sums or byte rates. An older unused feature helper
could make that substitution; it has been corrected and is covered by regression
tests.

Both models share training-only median imputation and standardization. Logistic
regression uses its default regularization and a 3,000-iteration limit. Random
Forest uses 200 trees and a minimum leaf size of two. Seeds 42–46 determine split
and estimator randomness. Hyperparameters were fixed rather than selected using
the final held-out categories. The separate full-data inference artifacts are not
used to compute test metrics.

### 3.2 Evaluation designs

**Random baseline:** a stratified 75/25 flow split establishes within-dataset
performance. It does not establish flow independence or session generalization.

**Exact-feature-group baseline:** identical numeric feature vectors stay on the
same side of the split, even when they have different labels. This removes one
form of direct feature overlap. It cannot recover real session boundaries or
remove correlation among nonidentical flows.

**Full-category LOAO:** train on six VPN application categories and test all flows
from the seventh. The earlier study includes five stratified training bootstrap
runs, with fixed category tests, and full-training controls. Here “application”
means application category, not a held-out named product.

**Matched-category comparison:** for each category and seed, reserve 25% of that
category's flows as test data. Both conditions use exactly those test rows. The
unseen condition trains on the other six categories. The seen condition includes
remaining flows from the target category and samples other-category flows to
match the unseen condition's total training row count. Exact test feature vectors
are purged from both training candidates. There are 35 seen/unseen pairs per
model. Training composition still differs by design, and class ratios need not
be identical, so the experiment does not isolate a single causal mechanism.

**Duration ablation:** remove the raw VPN duration column and repeat full-category
LOAO at seed 42. Other timing and rate fields remain. This is a diagnostic
sensitivity check, not a complete removal of timing information.

### 3.3 Metrics and uncertainty

Macro-F1 is the main summary measure. Accuracy, macro-precision, macro-recall,
per-class precision/recall/F1/support, majority-class baselines and confusion
matrices are retained. The generalization drop is seen macro-F1 minus unseen
macro-F1 on matched tests. Means across categories weight each category equally.
Standard deviations measure variation across five splits or resamples; they are
not confidence intervals over independent sessions. No significance claim is made
from overlapping split repetitions.

## 4. Historical results

### 4.1 VPN baselines

In the earlier five-seed random-split study, Random Forest averaged 92.45%
accuracy and macro-F1 0.924; logistic regression averaged 61.70% and 0.604.
The new exact-feature-group VPN baseline averages 92.63% accuracy and macro-F1
0.926 for Random Forest, compared with 60.79% and 0.595 for logistic regression.
The small differences between split designs should not be interpreted as an
improvement caused by grouping. They show that exact-vector overlap alone does
not account for the high Random Forest within-dataset score.

### 4.2 Matched application-category results

| Model | Mean category-seen macro-F1 | Mean category-unseen macro-F1 | Mean drop |
| --- | ---: | ---: | ---: |
| Logistic regression | 0.509 | 0.396 | 0.113 |
| Random Forest | 0.902 | 0.535 | 0.367 |

Values average the seven category means, each based on five splits. Random Forest
has a positive drop in all 35 matched pairs. Its mean category drops are 0.291 for
browsing, 0.263 for chat, 0.226 for email, 0.245 for file transfer, 0.494 for P2P,
0.443 for streaming, and 0.606 for VoIP. Logistic regression has positive drops
in 28 of 35 pairs; its streaming mean is slightly negative. A weaker baseline can
therefore have less room to fall, so drop size alone is not a model-ranking metric.

![Matched category comparison](completion_study/matched_comparison.png)

![Generalization drops](completion_study/generalization_drop.png)

The full-category LOAO and matched experiments use different test populations and
training procedures. Their numbers must not be interchanged. Complete per-run
results and each design's definition are retained in the corresponding reports.

### 4.3 Error patterns and ablation

The earlier full-category bootstrap experiment shows a particularly weak VPN
recall for Random Forest VoIP, approximately 11.0%, despite mean accuracy near
58.0%. Its direct recall is approximately 95.7%. This is a concrete example of
class imbalance and asymmetric errors being hidden by an overall accuracy figure.
Those recall values belong to that earlier design, not the new matched tests.

Across seven full-category holdouts at seed 42, removing only duration changes
Random Forest's mean macro-F1 from 0.534 to 0.538. Logistic regression changes
from 0.397 to 0.475. Thus the severe Random Forest category-transfer failure is
not removed by this single-column ablation. Multiple related timing fields remain,
and this experiment does not establish which features encode application identity.

### 4.4 Tor baselines

| Model | Random accuracy | Random macro-F1 | Feature-group accuracy | Feature-group macro-F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic regression | 92.36% | 0.864 | 92.35% | 0.863 |
| Random Forest | 99.01% | 0.983 | 98.90% | 0.981 |

These are five-split means. The high Random Forest score is promising for this
historical binary task, but correlated captures and collection artifacts remain
possible explanations. Tor application LOAO cannot be constructed from Tor-only
application labels. Neither the Tor baseline nor the VPN baseline is evidence
for a joint three-class classifier.

![Tor baselines](completion_study/tor_baselines.png)

## 5. Temporal and combined-shift readiness

The transfer evaluator checks a documented feature contract, chronology, task
labels, sessions, provenance, finite numeric values and exact cross-period feature
overlap. Compatibility requires extractor versions, feature units/definitions,
flow rules and a local hashed fixture-verification report. The pending contract
is rejected by default. After verification, models fit historical data only and
score modern flows overall, by category and by session. Additional models exclude
one historical category to evaluate the combined shift.

Synthetic tests establish that modern features do not influence fitted scaling
and that held-out categories remain absent from combined-shift training. These
are software checks only. No real modern captures have been supplied, so no
measured temporal score, temporal drop, or combined-shift conclusion is reported.
Even a future controlled modern collection will confound time with environment,
application versions, device and VPN provider/protocol differences.

## 6. Threats to validity

The strongest limitation is absent historical capture provenance. Exact duplicate
removal and feature-vector grouping reduce specific overlap risks while leaving
correlated flows. The result is category generalization within historical exports,
not deployment performance on independent sessions. Class balance differs across
categories. Matched row counts do not match all training distributions. Repeated
seeds reuse observations, making naive independent-sample confidence intervals
inappropriate. Native VPN/Tor schemas and timeouts are not fully reconciled.
NonTor is not automatically interchangeable with Non-VPN. The ablation is narrow,
and the model set does not exhaust possible classifiers.

## 7. Reproducibility

`python run_all.py` runs tests, historical export, the 198-evaluation validation
study, figures, arithmetic/split checks and four frozen full-data model artifacts.
Data, configuration, source and environment fingerprints accompany the results.
Per-run predictions are local ignored checkpoints. Compact results, readable
tables and figures are repository artifacts. The saved-result validator
reconstructs metrics from confusion matrices, checks detailed predictions, and
checks all 70 matched split pairs. Raw datasets are never modified or committed.

The initial 80-run VPN study and its 14 full-training controls remain available
for comparison, with their separate protocol clearly stated. All reported numbers
in this draft are historical observations; pending data-dependent results are
explicitly distinguished from implementation readiness.

## 8. Remaining work before submission

Obtain one small direct/VPN pilot and verify its feature extraction by October 29.
Resolve feasibility by November 2, finish any credible modern evaluation by
November 9, then integrate results or state the limitation explicitly. Complete
report revision, instructor scope agreement, independent reproduction and the
presentation before the December 5 deadline. Do not substitute artificial sessions
or reissued historical datasets for the missing temporal evidence.

## References

1. Draper-Gil, G., Lashkari, A. H., Mamun, M. S. I., and Ghorbani, A. A. (2016).
   *Characterization of Encrypted and VPN Traffic Using Time-Related Features.*
   ICISSP, pp. 407–414. Dataset and citation information:
   [ISCXVPN2016](https://www.unb.ca/cic/datasets/vpn.html).
2. Lashkari, A. H., Draper-Gil, G., Mamun, M. S. I., and Ghorbani, A. A. (2017).
   *Characterization of Tor Traffic Using Time Based Features.* ICISSP.
   Dataset and citation information:
   [ISCXTor2016](https://www.unb.ca/cic/datasets/tor.html).
3. Canadian Institute for Cybersecurity. *CIC-Darknet2020 dataset description.*
   [Official dataset page](https://www.unb.ca/cic/datasets/darknet2020.html).

The linked dataset descriptions were checked for provenance; full papers were
not retrievable in this session (publisher access returned HTTP 403). This draft
does not claim to reproduce or outperform their published experiments.
