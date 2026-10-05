# p01-trustworthy-ml — Trustworthy ML: Compare Models Without Cheating

## Goal

Build a classification comparison that is **fair, reproducible, and reviewable** across several classical model families.

You will compare a trivial baseline with logistic regression, a decision tree, a Random Forest, and gradient boosting while keeping the information boundary, validation procedure, and final test conditions fixed.

The goal is not to choose a model because one headline metric is largest. The goal is to explain what the evidence supports and what tradeoffs remain.

## Prerequisites

Complete Level 1 through **L1.18 — Real-World Tabular ML: Pipelines and Model Review**.

You should be able to use:

- train/test splits and training-only cross-validation;
- accuracy, precision, recall, and class-imbalance reasoning;
- pipelines and data-dependent preprocessing;
- leakage and overfitting checks;
- decision trees and depth;
- Random Forest bagging, feature randomness, and aggregation;
- gradient boosting as sequential error correction;
- reproducible experiment records.

This is a local Python Builder project. If repository roots, virtual environments, or package installation are new, read `projects/PROJECT_WORKBENCH.md` before continuing.

## Data and provenance

`data/student_outcomes.csv` is a deterministic **synthetic educational fixture authored for this repository**. It contains no real student records.

Columns:

- `student_id` — row identifier; do not use it as a predictive feature.
- `practice_hours` — allowed numeric feature; some rows are intentionally missing.
- `attendance_rate` — allowed numeric feature; some rows are intentionally missing.
- `prior_quiz` — allowed numeric feature; some rows are intentionally missing.
- `study_track` — allowed categorical feature with intentional missing values.
- `region` — allowed categorical feature with intentional missing values.
- `certificate_issued` — **forbidden leaky feature** created after the outcome.
- `completed` — target.

The fixture contains 80 rows with a 25% positive class. The imbalance is deliberate: a majority-only baseline can look respectable on accuracy while having zero recall for the positive class. Missing values and categories are also deliberate so the project must exercise the Level 1.18 tabular workflow rather than collapsing back to a clean numeric matrix.

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r projects/starters/l01/requirements.txt
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Start

```bash
python projects/starters/l01/trustworthy_ml.py
```

The starter creates one fixed train/test split and one leak-safe mixed-type preprocessing recipe:

- numeric columns: median imputation, then scaling;
- categorical columns: most-frequent imputation, then one-hot encoding;
- all learned preprocessing remains inside each candidate pipeline and is refit inside each training-only cross-validation fold.

It gives you **one worked candidate**: logistic regression. Its training-only cross-validation evidence shows the format you should preserve. The starter intentionally does **not** add the decision tree, Random Forest, or gradient-boosting candidates, does not choose a learned model, and does not score a learned candidate on the final test set.

Your Builder work is to:

1. add the three missing model families with the same `make_candidate(...)` preprocessing boundary;
2. record each candidate's important settings;
3. compare all four learned candidates under the same training-only cross-validation;
4. state decision costs and write your selection criteria **before** opening learned-model final-test evidence;
5. fit only the selected candidate on all training rows and evaluate it once on the final test set;
6. update the experiment record so candidate settings, validation evidence, selection policy, selected family, and final evidence all match the run;
7. run one isolated bad experiment with `certificate_issued`, explain the suspicious improvement, and restore the clean feature set.

The reference solution contains one complete example policy. It is evidence of one valid workflow, not a required winner or a policy to copy without justification.

## Required deliverables

1. **Prediction contract**
   - state the target and prediction moment;
   - list allowed features;
   - explain why `certificate_issued` is forbidden.

2. **Fair evaluation and preprocessing**
   - preserve the fixed final test boundary;
   - keep numeric/categorical imputation and one-hot encoding inside the fitted pipeline;
   - use training-only validation for candidate comparison so preprocessing is refit inside each fold;
   - do not choose among candidate families by repeatedly checking final-test results;
   - keep the split and evaluation rules the same across models.

3. **Model-family comparison**
   - keep the majority baseline;
   - compare logistic regression;
   - compare a decision tree;
   - compare a Random Forest;
   - compare gradient boosting;
   - explain at least one practical tradeoff among them.

4. **Metrics and imbalance reasoning**
   - report accuracy, precision, recall, and F1 as validation evidence;
   - inspect class frequencies;
   - state which error type matters more for your interpretation;
   - write explicit selection criteria before opening learned-model final-test evidence;
   - use more than one relevant signal or constraint when your stated decision costs require it;
   - do not choose a model from one headline metric alone.

5. **Failure and overfitting analysis**
   - inspect training/validation behavior or another overfitting signal;
   - include one intentional bad experiment, such as temporarily adding `certificate_issued`;
   - explain why the suspicious improvement is invalid;
   - restore the clean feature set.

6. **Reproducibility record**
   - data path/revision and target;
   - split strategy and seed;
   - preprocessing and fitting boundary;
   - candidate settings for every compared family;
   - validation procedure, metrics, and evidence;
   - the selection policy written before final testing;
   - selected candidate;
   - baseline and selected-model final held-out metrics.

7. **Short model-review memo**
   - state a bounded recommendation for further testing;
   - cite at least three pieces of evidence;
   - name at least one limitation;
   - explain why the selected model is preferable under your stated criteria rather than merely reporting that it has the largest score.

## Validation

Run:

```bash
python projects/tests/l01/test_project.py
python projects/tests/l01/test_reference.py
```

Then run your own project script from a clean shell and save the evidence used in your review.

The starter structural test intentionally expects an **unfinished Builder starter**: one worked logistic candidate, safe preprocessing, no automatic model selection, and no learned-model final-test result. The reference test checks the complete four-family workflow. Neither test decides which family your own review should prefer.

## Expected success evidence

A complete submission shows:

- no train/test ID overlap;
- the forbidden feature absent from the clean comparison;
- one common training-only validation procedure across learned candidates;
- numeric and categorical missing values handled inside the pipeline;
- one-hot encoding fitted without leaking validation/test categories;
- baseline, logistic, tree, Random Forest, and boosting coverage;
- a selection policy stated before the learned-model final test is opened;
- validation evidence that uses multiple relevant signals rather than one headline score;
- baseline plus selected-model final metrics only after selection;
- at least one diagnosed failure or overfitting signal;
- a repeatable experiment record whose settings and evidence match the actual run;
- a conclusion tied to evidence and limitations.

## Resource expectations

This project is CPU-only and small. No cloud account, token, secret, or external model asset is required.
