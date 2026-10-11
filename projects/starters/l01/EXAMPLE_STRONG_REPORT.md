# p01 Trustworthy ML — strong evidence report (example)

> **Format example only.** Do not copy this report or treat its selected model as the required winner. **Use your own numbers and your own observations.** This example is based on the repository's 80-row synthetic `student_outcomes.csv`, fixed split, and one independently reproducible candidate comparison.

## Contract, split, and data audit

- **Question:** predict `completed` before a certificate is issued. The target is `completed`; numeric inputs are `practice_hours`, `attendance_rate`, `prior_quiz`; categorical inputs are `study_track`, `region`. The `student_id` is not a predictor. `certificate_issued` is forbidden future information and excluded from the clean model.
- **Reproduction environment for these example numbers:** Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, CPU; other supported package versions may produce slightly different model metrics.
- **Fixture:** `projects/starters/l01/data/student_outcomes.csv`, 80 synthetic rows, 20 positives (25%). Missing values: practice hours 5, attendance 6, prior quiz 7, track 6, region 5.
- **Split:** stratified 70/30 with `random_state=42` (56 training, 24 final test rows, no ID overlap). The four models all use `StratifiedKFold(n_splits=4, shuffle=True, random_state=42)` **only on training rows**.
- **Leak-safe preprocessing:** each model owns a `Pipeline`: numeric median imputation and scaling; categorical most-frequent imputation and one-hot encoding. These steps refit within each CV training fold.

## Model comparison before final testing

Settings: logistic regression `max_iter=500`; decision tree `max_depth=3`; Random Forest `n_estimators=80, max_depth=4, max_features="sqrt", bootstrap=True`; gradient boosting `n_estimators=60, learning_rate=0.05, max_depth=2`. All use seed 42.

| Learned candidate | CV accuracy | CV precision | CV recall | CV F1 | Train − validation recall gap |
|---|---:|---:|---:|---:|---:|
| Logistic regression | 0.857 | 0.813 | 0.646 | 0.679 | 0.141 |
| Decision tree | 0.696 | 0.250 | 0.146 | 0.183 | 0.543 |
| Random Forest | 0.696 | 0.333 | 0.146 | 0.183 | 0.784 |
| Gradient boosting | 0.679 | 0.208 | 0.146 | 0.167 | 0.784 |

**Policy stated before opening learned-model final-test results:** because false negatives matter here, require CV recall ≥ 0.60 and precision ≥ 0.60, reject a train–validation recall gap over 0.25, then break ties by CV F1. Accuracy is context, not the sole selection metric. Under this example policy, **only logistic regression is eligible**. A shallow tree is interpretable, forests reduce variance through bagging, and boosting corrects errors sequentially, but their measured positive-class recall is insufficient in this run.

## Final held-out evidence (opened once after selection)

| Model | Test accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Majority-only baseline | 0.750 | 0.000 | 0.000 | 0.000 |
| Selected logistic regression | 0.875 | 0.800 | 0.667 | 0.727 |

The baseline looks acceptable on accuracy because 75% of labels are negative, but it misses every positive. The selected model improves positive recall under the **predeclared** rule; 24 final cases do not establish robustness outside this fixture.

## Intentional bad experiment and diagnosis

- **Failure check:** temporarily add `certificate_issued` (a post-outcome feature) and fit a depth-1 decision tree on the same seeded split. Observed leaky test accuracy is **1.000**.
- **Hypothesis:** the certificate is downstream of the label, so the apparent improvement is leakage, not useful information available at prediction time.
- **Single fix / verification:** remove the forbidden column and restore the five allowed features in every final candidate pipeline; refit without using that leaky outcome for selection. The clean selected model's held-out accuracy is 0.875, not 1.000.

## Reproduction and bounded decision

Run the documented project commands from the repository root after installing `projects/starters/l01/requirements.txt`. The starter's `python projects/tests/l01/test_project.py` checks **starter structure**, not completion of the expanded model comparison; verify your own added candidates, decision record, and final metrics separately. Record the exact Python/NumPy/scikit-learn versions, settings, CV summaries, selection policy, and script output with your own report.

**Decision:** use this logistic configuration for a further pilot on newly collected, temporally appropriate observations, not immediate production. Risks include the tiny synthetic dataset, small positive test count, shifted cohorts, and error-cost assumptions. Retest positive recall and calibrate the decision threshold on fresh validation data, without repeatedly searching the final test answers.

**Self-score prompt:** Can I substantiate the 100-point rubric's contract, split, all model families, metrics, leakage debug, reproducibility, and bounded recommendation before awarding top-band marks?
