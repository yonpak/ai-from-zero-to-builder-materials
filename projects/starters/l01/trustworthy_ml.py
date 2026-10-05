"""Starter for p01-trustworthy-ml.

This starter demonstrates a safe mixed-type pipeline and one training-only
validation example. The learner must extend the model-family comparison, define
selection criteria, and open the final test set only after choosing a candidate.
"""
from pathlib import Path
import csv

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = Path(__file__).parent / "data" / "student_outcomes.csv"
NUMERIC_FEATURES = ["practice_hours", "attendance_rate", "prior_quiz"]
CATEGORICAL_FEATURES = ["study_track", "region"]
ALLOWED_FEATURES = [
    "practice_hours",
    "attendance_rate",
    "prior_quiz",
    "study_track",
    "region",
]
FORBIDDEN_FEATURES = ["certificate_issued"]
TARGET = "completed"
RANDOM_STATE = 42
NUMERIC_COLUMNS = [0, 1, 2]
CATEGORICAL_COLUMNS = [3, 4]

with DATA_PATH.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))


def numeric_value(row, name):
    value = row[name].strip()
    return np.nan if value == "" else float(value)


def categorical_value(row, name):
    value = row[name].strip()
    return np.nan if value == "" else value


student_ids = np.array([int(row["student_id"]) for row in rows])
X = np.array(
    [
        [numeric_value(row, name) for name in NUMERIC_FEATURES]
        + [categorical_value(row, name) for name in CATEGORICAL_FEATURES]
        for row in rows
    ],
    dtype=object,
)
y = np.array([int(row[TARGET]) for row in rows], dtype=int)
positive_rate = float(y.mean())
missing_counts = {
    name: sum(row[name].strip() == "" for row in rows)
    for name in ALLOWED_FEATURES
}


def make_preprocessor(
    numeric_columns=NUMERIC_COLUMNS,
    categorical_columns=CATEGORICAL_COLUMNS,
):
    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric_columns,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                sparse_output=False,
                            ),
                        ),
                    ]
                ),
                categorical_columns,
            ),
        ],
        sparse_threshold=0.0,
    )


def make_candidate(model):
    return Pipeline(
        [
            ("preprocess", make_preprocessor()),
            ("model", model),
        ]
    )


(
    X_train,
    X_test,
    y_train,
    y_test,
    ids_train,
    ids_test,
) = train_test_split(
    X,
    y,
    student_ids,
    test_size=0.30,
    random_state=RANDOM_STATE,
    stratify=y,
)

# The starter gives one complete candidate as a worked pattern.
# Add decision tree, Random Forest, and gradient boosting yourself, using
# make_candidate(...) so every family keeps the same preprocessing boundary.
candidates = {
    "logistic": make_candidate(
        LogisticRegression(max_iter=500, random_state=RANDOM_STATE)
    ),
}

CANDIDATE_SETTINGS = {
    "logistic": {
        "model": "LogisticRegression",
        "max_iter": 500,
        "random_state": RANDOM_STATE,
    },
}

cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=RANDOM_STATE)
SCORING = {
    "accuracy": "accuracy",
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": make_scorer(recall_score, zero_division=0),
    "f1": make_scorer(f1_score, zero_division=0),
}


def validation_evidence(model):
    scores = cross_validate(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring=SCORING,
        return_train_score=True,
    )
    validation_recall = float(scores["test_recall"].mean())
    train_recall = float(scores["train_recall"].mean())
    return {
        "validation_accuracy": float(scores["test_accuracy"].mean()),
        "validation_precision": float(scores["test_precision"].mean()),
        "validation_recall": validation_recall,
        "validation_f1": float(scores["test_f1"].mean()),
        "train_recall": train_recall,
        "recall_gap": max(0.0, train_recall - validation_recall),
    }


# This is an example of the evidence table, not a completed model comparison.
# Extend it only with candidates evaluated under the same training-only CV.
validation_summary = {
    name: validation_evidence(model)
    for name, model in candidates.items()
}

baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)


def metrics(model):
    predictions = model.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
    }


# It is safe to inspect a fixed majority baseline now because it is not a
# candidate used for model-family selection. Do not score learned candidates on
# X_test until you have written your selection criteria and chosen one.
baseline_result = metrics(baseline)
split_overlap = sorted(set(ids_train).intersection(ids_test))

EXPERIMENT_RECORD = {
    "data": "projects/starters/l01/data/student_outcomes.csv",
    "target": TARGET,
    "allowed_features": ALLOWED_FEATURES,
    "split": {
        "test_size": 0.30,
        "random_state": RANDOM_STATE,
        "stratified": True,
    },
    "preprocessing": {
        "numeric": "median imputation, then StandardScaler",
        "categorical": "most-frequent imputation, then one-hot encoding",
        "fit_boundary": "inside each candidate Pipeline and CV training fold",
    },
    "candidate_settings": CANDIDATE_SETTINGS,
    "validation": {
        "method": "4-fold StratifiedKFold on training rows only",
        "metrics": list(SCORING),
        "evidence": validation_summary,
    },
    # Fill these only after you state decision costs and choose from validation.
    "selection_policy": None,
    "selected_candidate": None,
    "final_evidence": {
        "baseline": baseline_result,
        "selected": None,
    },
}

if __name__ == "__main__":
    print("Allowed features:", ALLOWED_FEATURES)
    print("Forbidden features:", FORBIDDEN_FEATURES)
    print("Positive-class rate:", round(positive_rate, 3))
    print("Missing values:", missing_counts)
    print("Train/test overlap:", split_overlap)
    print("Starter validation evidence:")
    for name, evidence in validation_summary.items():
        print(" ", name, {key: round(value, 3) for key, value in evidence.items()})
    print("Final-test majority baseline:", baseline_result)
    print("Experiment record:", EXPERIMENT_RECORD)
    print()
    print("Builder work remaining:")
    print("1. Add decision tree, Random Forest, and gradient boosting pipelines.")
    print("2. Compare all candidates under the same training-only CV.")
    print("3. Write selection criteria before scoring a learned model on X_test.")
    print("4. Fit only the selected family, record final evidence, and update the record.")
    print("5. Run and explain one isolated bad experiment with the forbidden feature.")
