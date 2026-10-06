# Results across five runs

Values are mean ± sample standard deviation, on a 0–1 scale. For example, 0.924 accuracy means 92.4% correct. The variation describes run sensitivity, not confidence intervals over independent sessions. Held-out rows use training bootstrap samples; the random baseline varies its split.

| Model | Evaluation | Accuracy | Macro-F1 | Macro-precision | Macro-recall |
| --- | --- | --- | --- | --- | --- |
| Logistic regression | Random baseline | 0.617 ± 0.016 | 0.604 ± 0.015 | 0.624 ± 0.019 | 0.611 ± 0.015 |
| Logistic regression | Browsing | 0.530 ± 0.005 | 0.450 ± 0.025 | 0.573 ± 0.015 | 0.530 ± 0.005 |
| Logistic regression | Chat | 0.502 ± 0.004 | 0.413 ± 0.008 | 0.430 ± 0.008 | 0.459 ± 0.004 |
| Logistic regression | Email | 0.609 ± 0.015 | 0.379 ± 0.006 | 0.316 ± 0.003 | 0.472 ± 0.012 |
| Logistic regression | File transfer | 0.524 ± 0.034 | 0.521 ± 0.031 | 0.568 ± 0.023 | 0.575 ± 0.027 |
| Logistic regression | P2P | 0.370 ± 0.017 | 0.294 ± 0.027 | 0.304 ± 0.065 | 0.439 ± 0.015 |
| Logistic regression | Streaming | 0.493 ± 0.014 | 0.492 ± 0.014 | 0.494 ± 0.015 | 0.494 ± 0.015 |
| Logistic regression | VoIP | 0.291 ± 0.001 | 0.226 ± 0.000 | 0.173 ± 0.001 | 0.327 ± 0.001 |
| Random Forest | Random baseline | 0.924 ± 0.002 | 0.924 ± 0.002 | 0.925 ± 0.002 | 0.924 ± 0.002 |
| Random Forest | Browsing | 0.618 ± 0.017 | 0.612 ± 0.018 | 0.626 ± 0.017 | 0.618 ± 0.017 |
| Random Forest | Chat | 0.669 ± 0.030 | 0.615 ± 0.042 | 0.702 ± 0.038 | 0.631 ± 0.033 |
| Random Forest | Email | 0.657 ± 0.012 | 0.578 ± 0.021 | 0.610 ± 0.018 | 0.581 ± 0.017 |
| Random Forest | File transfer | 0.704 ± 0.012 | 0.661 ± 0.017 | 0.659 ± 0.016 | 0.664 ± 0.020 |
| Random Forest | P2P | 0.438 ± 0.011 | 0.418 ± 0.015 | 0.477 ± 0.013 | 0.484 ± 0.009 |
| Random Forest | Streaming | 0.461 ± 0.023 | 0.446 ± 0.024 | 0.461 ± 0.026 | 0.466 ± 0.023 |
| Random Forest | VoIP | 0.580 ± 0.037 | 0.444 ± 0.084 | 0.617 ± 0.078 | 0.533 ± 0.042 |
