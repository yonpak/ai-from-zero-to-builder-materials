"""Reference evaluation for p01-trustworthy-ml.

This is one complete example, not a required winning-family answer. It keeps
mixed-type preprocessing inside each model pipeline, compares model families
with training-only cross-validation, applies an explicit constrained example
policy, and opens the final test set only for the baseline and selected model.
"""
from pathlib import Path
import csv

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
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
from sklearn.tree import DecisionTreeClassifier

DATA_PATH = Path(__file__).resolve().parents[2] / "starters" / "l01" / "data" / "student_outcomes.csv"
NUMERIC_FEATURES = ["practice_hours", "attendance_rate", "prior_quiz"]
CATEGORICAL_FEATURES = ["study_track", "region"]
FEATURES = [
    "practice_hours",
    "attendance_rate",
    "prior_quiz",
    "study_track",
    "region",
]
TARGET = "completed"
SEED = 42
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


X = np.array(
    [
        [numeric_value(row, name) for name in NUMERIC_FEATURES]
        + [categorical_value(row, name) for name in CATEGORICAL_FEATURES]
        for row in rows
    ],
    dtype=object,
)
y = np.array([int(row[TARGET]) for row in rows], dtype=int)
certificate_issued = np.array([int(row["certificate_issued"]) for row in rows], dtype=int)
positive_rate = float(y.mean())
missing_counts = {
    name: sum(row[name].strip() == "" for row in rows)
    for name in FEATURES
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


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=SEED, stratify=y
)

CANDIDATE_SETTINGS = {
    "logistic": {
        "model": "LogisticRegression",
        "max_iter": 500,
        "random_state": SEED,
    },
    "decision_tree": {
        "model": "DecisionTreeClassifier",
        "max_depth": 3,
        "random_state": SEED,
    },
    "random_forest": {
        "model": "RandomForestClassifier",
        "n_estimators": 80,
        "max_depth": 4,
        "max_features": "sqrt",
        "bootstrap": True,
        "random_state": SEED,
    },
    "gradient_boosting": {
        "model": "GradientBoostingClassifier",
        "n_estimators": 60,
        "learning_rate": 0.05,
        "max_depth": 2,
        "random_state": SEED,
    },
}

candidates = {
    "logistic": make_candidate(
        LogisticRegression(max_iter=500, random_state=SEED)
    ),
    "decision_tree": make_candidate(
        DecisionTreeClassifier(max_depth=3, random_state=SEED)
    ),
    "random_forest": make_candidate(
        RandomForestClassifier(
            n_estimators=80,
            max_depth=4,
            max_features="sqrt",
            bootstrap=True,
            random_state=SEED,
        )
    ),
    "gradient_boosting": make_candidate(
        GradientBoostingClassifier(
            n_estimators=60,
            learning_rate=0.05,
            max_depth=2,
            random_state=SEED,
        )
    ),
}

cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=SEED)
SCORING = {
    "accuracy": "accuracy",
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": make_scorer(recall_score, zero_division=0),
    "f1": make_scorer(f1_score, zero_division=0),
}

validation_summary = {}
for name, model in candidates.items():
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
    validation_summary[name] = {
        "validation_accuracy": float(scores["test_accuracy"].mean()),
        "validation_precision": float(scores["test_precision"].mean()),
        "validation_recall": validation_recall,
        "validation_f1": float(scores["test_f1"].mean()),
        "train_recall": train_recall,
        "recall_gap": max(0.0, train_recall - validation_recall),
    }

# Example decision criteria for this synthetic exercise. These are not universal
# thresholds and should be replaced when a different decision has different
# costs. Accuracy is still reported as context, but the stated policy focuses on
# finding positives, avoiding too many false alarms, and rejecting a large
# train-validation recall gap before using F1 as a final tie-break signal.
MIN_RECALL = 0.60
MIN_PRECISION = 0.60
MAX_RECALL_GAP = 0.25
SELECTION_POLICY = (
    "Example only: require validation recall >= 0.60, validation precision >= "
    "0.60, and train-validation recall gap <= 0.25; among eligible candidates, "
    "prefer higher validation F1. Accuracy is reported as context."
)


def meets_example_constraints(evidence):
    return (
        evidence["validation_recall"] >= MIN_RECALL
        and evidence["validation_precision"] >= MIN_PRECISION
        and evidence["recall_gap"] <= MAX_RECALL_GAP
    )


eligible_names = [
    name
    for name, evidence in validation_summary.items()
    if meets_example_constraints(evidence)
]
if not eligible_names:
    raise RuntimeError(
        "No candidate meets the example constraints; revise the policy rather than opening the final test set."
    )

selected_name = max(
    eligible_names,
    key=lambda name: validation_summary[name]["validation_f1"],
)
selected = candidates[selected_name].fit(X_train, y_train)
baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
preprocessed_feature_count = selected.named_steps["preprocess"].transform(X_train).shape[1]


def report(model):
    pred = model.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
    }


final_report = {
    "baseline": report(baseline),
    "selected": report(selected),
}

EXPERIMENT_RECORD = {
    "data": "projects/starters/l01/data/student_outcomes.csv",
    "target": TARGET,
    "features": FEATURES,
    "split": {
        "test_size": 0.30,
        "random_state": SEED,
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
    "selection_policy": SELECTION_POLICY,
    "eligible_candidates": eligible_names,
    "selected_candidate": selected_name,
    "final_evidence": final_report,
}

# Isolated failure demonstration: use the real future-only fixture column.
# Never use this pipeline for the final model.
X_leaky = np.column_stack([X, certificate_issued.astype(object)])
leaky_preprocessor = make_preprocessor(
    numeric_columns=[0, 1, 2, 5],
    categorical_columns=[3, 4],
)
leaky_train, leaky_test, ly_train, ly_test = train_test_split(
    X_leaky, y, test_size=0.30, random_state=SEED, stratify=y
)
leaky_model = Pipeline(
    [
        ("preprocess", leaky_preprocessor),
        ("model", DecisionTreeClassifier(max_depth=1, random_state=SEED)),
    ]
).fit(leaky_train, ly_train)
leaky_accuracy = float(leaky_model.score(leaky_test, ly_test))

if __name__ == "__main__":
    print("Positive-class rate:", round(positive_rate, 3))
    print("Missing values:", missing_counts)
    print("Preprocessed feature count:", preprocessed_feature_count)
    print("Selection policy:", SELECTION_POLICY)
    print("Validation evidence:")
    for name, evidence in validation_summary.items():
        print(" ", name, {key: round(value, 3) for key, value in evidence.items()})
    print("Eligible under example policy:", eligible_names)
    print("Selected:", selected_name)
    print("Final report:", final_report)
    print("Experiment record:", EXPERIMENT_RECORD)
    print("Intentional future-feature leak accuracy:", round(leaky_accuracy, 3))
