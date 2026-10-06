# Which class gets misclassified?

Direct means Non-VPN. Each value is the mean percentage across five runs. Correct and incorrect percentages for each actual class sum to 100%, apart from rounding.

| Model | Evaluation | Direct correctly identified | VPN correctly identified | Direct mistaken for VPN | VPN mistaken for direct |
| --- | --- | --- | --- | --- | --- |
| Logistic regression | Random baseline | 45.1% | 77.1% | 54.9% | 22.9% |
| Logistic regression | Browsing | 15.2% | 90.7% | 84.8% | 9.3% |
| Logistic regression | Chat | 13.0% | 78.7% | 87.0% | 21.3% |
| Logistic regression | Email | 0.0% | 94.5% | 100.0% | 5.5% |
| Logistic regression | File transfer | 71.0% | 43.9% | 29.0% | 56.1% |
| Logistic regression | P2P | 3.6% | 84.2% | 96.4% | 15.8% |
| Logistic regression | Streaming | 53.1% | 45.6% | 46.9% | 54.4% |
| Logistic regression | VoIP | 0.0% | 65.4% | 100.0% | 34.6% |
| Random Forest | Random baseline | 90.8% | 94.0% | 9.2% | 6.0% |
| Random Forest | Browsing | 49.8% | 73.8% | 50.2% | 26.2% |
| Random Forest | Chat | 34.4% | 91.7% | 65.6% | 8.3% |
| Random Forest | Email | 31.8% | 84.4% | 68.2% | 15.6% |
| Random Forest | File transfer | 55.8% | 77.1% | 44.2% | 22.9% |
| Random Forest | P2P | 21.6% | 75.1% | 78.4% | 24.9% |
| Random Forest | Streaming | 64.1% | 29.1% | 35.9% | 70.9% |
| Random Forest | VoIP | 95.7% | 11.0% | 4.3% | 89.0% |
