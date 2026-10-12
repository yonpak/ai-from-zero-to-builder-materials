# p01 Sample Reference Evaluation

This file demonstrates how to apply the rubric. It is not a required byte-identical answer.

## Prediction contract

Target: `completed`.

Prediction moment: before course completion is known and before any certificate is issued.

Allowed features in the clean model: `practice_hours`, `attendance_rate`, `prior_quiz`.

Rejected feature: `certificate_issued`. It is created after the outcome and therefore carries future/answer information.

**Rubric evidence:** full credit for prediction contract/feature audit.

## Evaluation design

- 70/30 stratified train/test split.
- `random_state=42`.
- Final test set is not used to choose the model.
- Four-fold stratified cross-validation on the training portion chooses between a scaled logistic-regression pipeline and a depth-2 decision tree.
- Selection metric in the sample is recall, representing a scenario where missed positive outcomes matter more than extra follow-up.

**Rubric evidence:** strong fair-split/validation evidence. A learner may choose another justified metric.

## Pipeline and candidates

- Baseline: `DummyClassifier(strategy="most_frequent")`.
- Candidate A: `StandardScaler` → `LogisticRegression`.
- Candidate B: `DecisionTreeClassifier(max_depth=2)`.

Scaling is contained inside Candidate A's pipeline, so each cross-validation fold fits the scaler using only that fold's training rows.

## Metrics

Run:

```bash
python projects/reference/l01/trustworthy_ml_reference.py
```

Use the printed held-out accuracy, precision, and recall as the sample evidence. Exact values can change if the fixture or library versions are intentionally revised, so the rubric judges the comparison procedure and interpretation rather than a hard-coded score.

## Intentional failure/debug path

The reference also creates a separate matrix that appends the target itself as a feature to imitate `certificate_issued`. The resulting score should look suspiciously strong.

Diagnosis: the model is reading information that would not exist at the prediction moment.

Fix: discard the leaky matrix and keep the final model on the three allowed features only.

**Rubric evidence:** full credit only if the learner explains the time/information boundary, not merely “because the instructions say so.”

## Sample decision

**Approve for the classroom fixture only, with limits.**

Evidence:

1. The selected model is chosen without using the final test labels for model selection.
2. Learned scaling stays inside a pipeline.
3. The final report includes multiple held-out metrics and a trivial baseline.
4. The leaky-feature experiment is isolated and rejected.

Limits:

- the dataset is synthetic and tiny;
- no subgroup/fairness analysis is meaningful on this fixture;
- the result should not be treated as evidence for a real student decision system.

## Example score

A submission following the same methodology, with clear reasoning and reproducibility evidence, would normally fall in the **90–100** band. A submission with correct code but no validation separation or leakage explanation should score substantially lower even if its final accuracy is high.
