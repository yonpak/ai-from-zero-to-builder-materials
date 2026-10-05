import importlib.util
from pathlib import Path

from sklearn.base import clone

ROOT = Path(__file__).resolve().parents[3]
STARTER = ROOT / "projects" / "starters" / "l01" / "trustworthy_ml.py"

spec = importlib.util.spec_from_file_location("p01_starter", STARTER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    check(module.split_overlap == [], "train/test IDs must not overlap")
    check("certificate_issued" not in module.ALLOWED_FEATURES, "leaky future feature must be excluded")
    check("certificate_issued" in module.FORBIDDEN_FEATURES, "forbidden feature must be documented")

    check(module.NUMERIC_FEATURES == ["practice_hours", "attendance_rate", "prior_quiz"], "numeric contract changed")
    check(module.CATEGORICAL_FEATURES == ["study_track", "region"], "categorical contract changed")
    check(0.15 <= module.positive_rate <= 0.35, "fixture should preserve a meaningful minority positive class")
    check(module.missing_counts["prior_quiz"] > 0, "numeric missing-value practice is required")
    check(module.missing_counts["study_track"] > 0, "categorical missing-value practice is required")

    check(set(module.candidates) == {"logistic"}, "starter should leave model-family expansion to the learner")
    check(set(module.validation_summary) == {"logistic"}, "starter should demonstrate CV with one candidate, not finish the comparison")
    check(set(module.SCORING) == {"accuracy", "precision", "recall", "f1"}, "starter evidence must show multiple metrics")
    check(not hasattr(module, "selected_name"), "starter must not auto-select a learned model")
    check(not hasattr(module, "final_report"), "starter must not open final-test evidence for a learned model")

    logistic = module.candidates["logistic"]
    check(list(logistic.named_steps) == ["preprocess", "model"], "logistic must own preprocessing inside its pipeline")
    transformers = {entry[0] for entry in logistic.named_steps["preprocess"].transformers}
    check(transformers == {"numeric", "categorical"}, "starter needs numeric and categorical preprocessing")

    fitted_logistic = clone(logistic).fit(module.X_train, module.y_train)
    transformed_count = fitted_logistic.named_steps["preprocess"].transform(module.X_train).shape[1]
    check(
        transformed_count > len(module.ALLOWED_FEATURES),
        "one-hot encoding should visibly expand the mixed-type feature space",
    )

    evidence = module.validation_summary["logistic"]
    expected_fields = {
        "validation_accuracy",
        "validation_precision",
        "validation_recall",
        "validation_f1",
        "train_recall",
        "recall_gap",
    }
    check(set(evidence) == expected_fields, "starter validation evidence is incomplete")
    for value in evidence.values():
        check(0.0 <= value <= 1.0, "starter validation evidence outside [0,1]")

    check(module.baseline_result["recall"] == 0.0, "majority baseline should expose minority-class failure")

    record = module.EXPERIMENT_RECORD
    check(
        set(record) == {
            "data",
            "target",
            "allowed_features",
            "split",
            "preprocessing",
            "candidate_settings",
            "validation",
            "selection_policy",
            "selected_candidate",
            "final_evidence",
        },
        "starter experiment record must expose the complete reproducibility template",
    )
    check(record["split"]["random_state"] == module.RANDOM_STATE, "experiment record must preserve split seed")
    check(record["allowed_features"] == module.ALLOWED_FEATURES, "experiment record must preserve features")
    check(set(record["candidate_settings"]) == {"logistic"}, "starter record should list the provided candidate settings")
    check(record["validation"]["metrics"] == list(module.SCORING), "record must name validation metrics")
    check(record["validation"]["evidence"] == module.validation_summary, "record must carry current validation evidence")
    check(record["selection_policy"] is None, "learner must define selection policy before final testing")
    check(record["selected_candidate"] is None, "starter must not preselect a model")
    check(record["final_evidence"]["baseline"] == module.baseline_result, "baseline evidence should be recorded")
    check(record["final_evidence"]["selected"] is None, "starter must leave learned final evidence unopened")

    print("p01 starter contract verification passed")
    print("Positive rate:", module.positive_rate)
    print("Missing values:", module.missing_counts)
    print("Starter validation:", module.validation_summary)
    print("Baseline final evidence:", module.baseline_result)


if __name__ == "__main__":
    main()
