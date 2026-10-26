# Local datasets and generated data

Raw files are local, ignored by Git, and must not be edited by preprocessing.

| Expected file | Purpose |
| --- | --- |
| `raw/Scenario B-ARFF.zip` | VPN/direct plus seven category labels; use the 15s member |
| `raw/Scenario-A-merged_5s.csv` | Binary Tor/NonTor flow labels |
| `raw/Scenario-B-merged_5s.csv` | Category-labeled Tor flows overlapping Scenario A |

Obtain the datasets from the official [VPN](https://www.unb.ca/cic/datasets/vpn.html)
and [Tor](https://www.unb.ca/cic/datasets/tor.html) pages and cite their papers.
The other locally downloaded VPN archives are not pooled into the experiments.

`python prepare_datasets.py` creates `processed/historical/vpn.csv`, `tor.csv`,
and `quality_report.json`. These are native numeric features plus available class
and category metadata. Tor lacks NonTor category metadata, so no category column
is invented. The year 2016 records dataset identity, not an observed per-flow date.

Exact duplicates are removed before splitting. IP addresses, ports, target labels,
application categories, years and source identifiers are excluded from model input.
Infinite historical values become missing values and are imputed from training only.

`processed/completion_study/<run signature>/` contains indented per-run prediction
JSON checkpoints. The signature includes data, configuration, environment and
source fingerprints. `reports/completion_study/` contains compact readable results.

Modern data should live in `raw/modern/`, with one real capture session per file
and a populated manifest based on `reports/modern_capture_manifest.csv`. No such
capture files currently exist. Do not use modern data for fitting preprocessing.
