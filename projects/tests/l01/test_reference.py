#!/usr/bin/env python3
"""Verify the Level 1 reference project preserves the evaluation contract."""

from __future__ import annotations

import ast
import importlib.util
import math
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "projects" / "reference" / "l01" / "trustworthy_ml_reference.py"

spec = importlib.util.spec_from_file_location("l01_reference", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

sys.path.insert(0, str(ROOT / "projects" / "tests"))
from failure_fixture import mutated_copy


EXPECTED_FEATURES = [
    "practice_hours",
    "attendance_rate",
    "prior_quiz",
    "study_track",
    "region",
]


def require_clean_feature_contract(candidate_module) -> None:
    if candidate_module.FEATURES != EXPECTED_FEATURES:
        raise AssertionError(f"clean FEATURES must be {EXPECTED_FEATURES!r}")
    if "certificate_issued" in candidate_module.FEATURES:
        raise AssertionError("future-only certificate_issued leaked into clean features")


def require_clean_feature_source(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "FEATURES" for target in node.targets):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            raise AssertionError("FEATURES must be a reviewable literal list in the reference contract")
        if value != EXPECTED_FEATURES:
            raise AssertionError(f"clean FEATURES must be {EXPECTED_FEATURES!r}")
        return
    raise AssertionError("reference contract must declare FEATURES")


class ReferenceProjectTests(unittest.TestCase):
    def test_prediction_boundary_excludes_leaky_feature(self):
        require_clean_feature_contract(module)
        self.assertNotIn("certificate_issued", module.FEATURES)
        self.assertEqual(module.TARGET, "completed")

    def test_mixed_type_fixture_exercises_level_1_tabular_skills(self):
        self.assertEqual(module.NUMERIC_FEATURES, ["practice_hours", "attendance_rate", "prior_quiz"])
        self.assertEqual(module.CATEGORICAL_FEATURES, ["study_track", "region"])
        self.assertGreaterEqual(module.positive_rate, 0.15)
        self.assertLessEqual(module.positive_rate, 0.35)
        self.assertGreater(module.missing_counts["prior_quiz"], 0)
        self.assertGreater(module.missing_counts["study_track"], 0)
        self.assertGreater(module.preprocessed_feature_count, len(module.FEATURES))

    def test_intentional_failure_fixture_rejects_leaky_feature(self):
        with mutated_copy(
            MODULE_PATH,
            (
                '    "region",\n]',
                '    "region",\n    "certificate_issued",\n]',
            ),
            filename="trustworthy_ml_reference.py",
        ) as broken:
            with self.assertRaises(AssertionError):
                require_clean_feature_source(broken)

    def test_every_candidate_owns_the_same_preprocessing_boundary(self):
        for name, candidate in module.candidates.items():
            self.assertEqual(list(candidate.named_steps), ["preprocess", "model"], name)
            transformer_names = {entry[0] for entry in candidate.named_steps["preprocess"].transformers}
            self.assertEqual(transformer_names, {"numeric", "categorical"}, name)

    def test_model_family_comparison_uses_multiple_validation_signals(self):
        expected = {"logistic", "decision_tree", "random_forest", "gradient_boosting"}
        self.assertEqual(set(module.candidates), expected)
        self.assertEqual(set(module.CANDIDATE_SETTINGS), expected)
        self.assertEqual(set(module.validation_summary), expected)
        self.assertEqual(set(module.SCORING), {"accuracy", "precision", "recall", "f1"})

        for evidence in module.validation_summary.values():
            self.assertEqual(
                set(evidence),
                {
                    "validation_accuracy",
                    "validation_precision",
                    "validation_recall",
                    "validation_f1",
                    "train_recall",
                    "recall_gap",
                },
            )
            for value in evidence.values():
                self.assertTrue(math.isfinite(value))
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)

    def test_example_policy_uses_real_constraints_before_f1(self):
        passing = {
            "validation_recall": 0.70,
            "validation_precision": 0.70,
            "recall_gap": 0.10,
        }
        self.assertTrue(module.meets_example_constraints(passing))

        for field, value in [
            ("validation_recall", module.MIN_RECALL - 0.01),
            ("validation_precision", module.MIN_PRECISION - 0.01),
            ("recall_gap", module.MAX_RECALL_GAP + 0.01),
        ]:
            evidence = dict(passing)
            evidence[field] = value
            self.assertFalse(module.meets_example_constraints(evidence), field)

        expected_eligible = [
            name
            for name, evidence in module.validation_summary.items()
            if module.meets_example_constraints(evidence)
        ]
        self.assertEqual(module.eligible_names, expected_eligible)
        self.assertTrue(module.eligible_names)
        self.assertLess(len(module.eligible_names), len(module.candidates))
        self.assertIn(module.selected_name, module.eligible_names)
        self.assertEqual(
            module.selected_name,
            max(
                module.eligible_names,
                key=lambda name: module.validation_summary[name]["validation_f1"],
            ),
        )

    def test_reference_exposes_an_overfitting_signal(self):
        self.assertTrue(any(
            evidence["recall_gap"] > 0
            for evidence in module.validation_summary.values()
        ))

    def test_final_test_is_reserved_for_baseline_and_selected_model(self):
        self.assertEqual(set(module.final_report), {"baseline", "selected"})
        self.assertEqual(module.final_report["baseline"]["recall"], 0.0)
        self.assertGreater(module.final_report["selected"]["recall"], 0.0)
        for model_name, metrics in module.final_report.items():
            self.assertEqual(set(metrics), {"accuracy", "precision", "recall", "f1"})
            for metric_name, value in metrics.items():
                self.assertTrue(math.isfinite(value), f"{model_name} {metric_name} is not finite")
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)

    def test_experiment_record_is_complete_and_matches_run(self):
        record = module.EXPERIMENT_RECORD
        self.assertEqual(record["target"], module.TARGET)
        self.assertEqual(record["features"], module.FEATURES)
        self.assertEqual(record["split"]["random_state"], module.SEED)
        self.assertEqual(record["candidate_settings"], module.CANDIDATE_SETTINGS)
        self.assertEqual(record["validation"]["metrics"], list(module.SCORING))
        self.assertEqual(record["validation"]["evidence"], module.validation_summary)
        self.assertEqual(record["selection_policy"], module.SELECTION_POLICY)
        self.assertEqual(record["eligible_candidates"], module.eligible_names)
        self.assertEqual(record["selected_candidate"], module.selected_name)
        self.assertEqual(record["final_evidence"], module.final_report)

    def test_intentional_leak_demo_uses_the_future_only_fixture_column(self):
        self.assertEqual(module.X.shape[1], len(module.FEATURES))
        self.assertEqual(module.X_leaky.shape[1], len(module.FEATURES) + 1)
        self.assertTrue(np.array_equal(module.X_leaky[:, -1].astype(int), module.certificate_issued))
        self.assertGreaterEqual(module.leaky_accuracy, 0.95)


if __name__ == "__main__":
    unittest.main()
