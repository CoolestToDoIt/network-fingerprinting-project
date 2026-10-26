# Frozen historical models

Four fitted models are saved locally under `models/historical/`, outside Git.
Each has a readable JSON card here and a matching local sidecar JSON. These models
were fitted on all available historical training data for later research inference;
they were not used to generate the held-out evaluation scores.

| Task | Models | Training flows | Labels |
| --- | --- | ---: | --- |
| VPN/direct | Logistic regression; Random Forest | 18,074 | 0 = Non-VPN, 1 = VPN |
| Tor/NonTor | Logistic regression; Random Forest | 83,701 | 0 = NonTor, 2 = Tor |

The JSON cards list exact ordered feature names, dataset/model fingerprints,
software versions, seed, intended use, and limitations. Model SHA-256 values refer
to the most recently generated local artifacts. Refit with `python freeze_models.py`
to regenerate both model files and cards together.

These are separate binary classifiers, not an integrated three-class model.
Feature units and extraction conventions must be verified before using modern
flows. The artifacts do not supply session independence or evidence of modern
traffic performance. Joblib files are binary executable serialization: load only
artifacts you generated or otherwise trust.
