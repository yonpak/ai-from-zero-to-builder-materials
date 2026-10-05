# p01-trustworthy-ml Rubric

**Project:** Trustworthy ML: Compare Models Without Cheating  
**Level:** 1  
**Total:** 100 points

This rubric maps to the expanded Level 1 exit skills: preserve information boundaries, compare major classical model families fairly, use imbalance-aware metrics, diagnose leakage/overfitting, and reproduce the full experiment.

| Criterion | Points | Observable evidence |
|---|---:|---|
| Prediction contract and feature audit | 15 | Target and prediction moment are explicit; allowed features are justified; `certificate_issued` is rejected as future/target leakage. |
| Fair split and validation design | 20 | Final test set stays outside fitting/model selection; one training-only validation design is shared by candidates; selection criteria are written before learned-model final testing; split strategy and seed are recorded. |
| Model-family comparison and pipelines | 20 | Majority baseline plus logistic regression, decision tree, Random Forest, and gradient boosting are compared; numeric/categorical imputation, scaling, and one-hot encoding stay inside each fitted pipeline; tree/ensemble tradeoffs are explained. |
| Metrics and class-imbalance interpretation | 15 | Accuracy, precision, recall, and F1 are read as evidence; class frequency and error costs are discussed; selection criteria use the signals or constraints justified by those costs rather than one headline metric. |
| Leakage and overfitting debug path | 15 | An intentional bad experiment is isolated, diagnosed, and removed; train/validation behavior or another overfitting signal such as the recorded recall gap is inspected. |
| Reproducibility | 10 | Data source, target/features, split, seed, preprocessing boundary, candidate settings, validation method/metrics/evidence, selection policy, selected candidate, and final evidence are sufficient to repeat the result. |
| Communication and model-review decision | 5 | The conclusion cites evidence, names limitations, and explains the selection criteria instead of treating the largest single score as sufficient. |

## Performance anchors

### 90–100 — Trustworthy and reproducible

The experiment boundary is clean, mixed-type preprocessing is refit inside the training boundary, all required model families are compared under the same training-only validation procedure, selection criteria are stated before learned-model final testing, and the conclusion explains metrics, tradeoffs, and limitations.

### 75–89 — Mostly trustworthy

Core workflow is correct, but one area is weak: family comparison, validation design, imbalance reasoning, failure analysis, or reproducibility. No final result depends on the leaky feature.

### 60–74 — Partial evidence

The learner can fit models and report scores, but model-family comparison or evaluation reasoning is incomplete. Examples include inconsistent splits, missing baseline, preprocessing outside the intended boundary, or choosing from one metric without discussing error costs.

### Below 60 — Not yet trustworthy

The final comparison uses `certificate_issued`, repeatedly selects models on the final test set, changes evaluation conditions between candidates, or cannot be reproduced.

## Required failure scenario

The submission must intentionally demonstrate **one broken experiment** and then fix it. The recommended scenario is to add `certificate_issued` temporarily and observe the suspiciously strong result. Full credit requires explaining why that feature would not exist at prediction time and confirming it is absent from the final clean model.

## Human-judgment guidance

Do not require byte-identical metrics or a particular winning family. Grade the fairness of the boundary, the quality of the evidence, the model-family reasoning, debugging, and reproducibility.
