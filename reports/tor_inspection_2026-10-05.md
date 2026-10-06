# Tor CSV inspection — October 5, 2026

The downloaded CSVs support an initial Tor classifier without PCAP processing.

- `Scenario-A-merged_5s.csv`: 84,194 rows, 29 columns; 69,686 NonTor and
  14,508 Tor labels. There are 493 exact duplicate rows and two missing cells.
- `Scenario-B-merged_5s.csv`: 14,508 rows, 29 columns; application-only labels
  (audio, browsing, chat, file transfer, mail, P2P, video, VoIP). There are 30
  exact duplicates. This file alone does not support binary Tor/NonTor LOAO.
- Neither file supplies capture-session IDs. Endpoints are not session IDs.

A preliminary stratified random baseline used Scenario A, removed exact duplicates
before splitting, and excluded IP addresses, ports, and target labels. Logistic
regression used 24 numeric features, including protocol, duration, rates,
interarrival times, active times, and idle times. Imputation and scaling were fit
only on training data. Seed=42; 62,775 training and 20,926 test flows.

| Accuracy | Macro-F1 | Macro-precision | Macro-recall |
| ---: | ---: | ---: | ---: |
| 92.30% | 0.8625 | 0.8707 | 0.8549 |

Confusion matrix (rows=true, columns=predicted; order NonTor, Tor):

| | Predicted NonTor | Predicted Tor |
| --- | ---: | ---: |
| Actual NonTor | 16,596 | 710 |
| Actual Tor | 902 | 2,718 |

This is a flow-random baseline, not a generalization result. Correlated flows can
still cross partitions despite exact deduplication. The majority-class accuracy
on the test set is approximately 82.70%. Tor and VPN baseline numbers should not
be interpreted as a direct comparison: datasets, features, and timeout variants
differ. The CSV filename indicates 5s; exact feature units and extractor settings
still need confirmation against source documentation before harmonization.

Full metrics/predictions: `data/processed/tor/baseline_metrics.json`.
Inspection, hashes and compact metrics: `reports/tor_inspection_2026-10-05.json`.
Loader: `load_tor_dataset` in `data_loaders.py`. All 11 tests pass.

Next: verify feature units and definitions, establish reliable provenance for
application labels on both Tor and NonTor flows, and recover real session IDs.
Do not concatenate Scenario A/B or assume row order establishes a label join.
