#!/usr/bin/env python3
"""Objective validator for p00-data-detective learner submissions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("p00_submission", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load submission: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def validate(module):
    require(module.predict(4, 4) is True, "predict(4, 4) should be True")
    require(module.predict(3, 4) is False, "predict(3, 4) should be False")

    rows = [(1, False), (3, True), (5, True)]
    require(module.count_mistakes(rows, 3) == 0, "count_mistakes should compare predictions with labels")
    require(module.count_mistakes(rows, 5) == 1, "count_mistakes should detect a wrong prediction")

    threshold = module.choose_best_threshold(module.TRAIN_EXAMPLES)
    require(threshold == 4, f"expected deterministic best training threshold 4, got {threshold!r}")

    clean_model_mistakes = module.count_mistakes(module.TEST_EXAMPLES, threshold)
    require(clean_model_mistakes == 0, f"expected 0 clean held-out mistakes, got {clean_model_mistakes}")
    require(module.baseline_mistakes(module.TEST_EXAMPLES) == 2, "majority baseline should make 2 held-out mistakes")

    noisy_mistakes = module.count_mistakes(module.NOISY_TEST_EXAMPLES, threshold)
    require(noisy_mistakes == 1, "intentional noisy scenario should expose exactly one failure")

    report = module.build_report()
    for key in ("threshold", "model_mistakes", "baseline_mistakes", "conclusion"):
        require(key in report, f"report is missing {key}")
    require(report["threshold"] == 4, "report threshold should come from training data")
    require(report["model_mistakes"] == 0, "report should evaluate clean held-out examples")
    require(report["baseline_mistakes"] == 2, "report should include the baseline on the same held-out examples")
    require(isinstance(report["conclusion"], str) and len(report["conclusion"].strip()) >= 20, "write a meaningful cautious conclusion")


def main(argv):
    if len(argv) != 2:
        print("Usage: python projects/tests/l00/validate_submission.py PATH_TO_DATA_DETECTIVE.py", file=sys.stderr)
        return 2
    path = Path(argv[1]).resolve()
    if not path.is_file():
        print(f"Submission not found: {path}", file=sys.stderr)
        return 2
    try:
        validate(load_module(path))
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: p00-data-detective objective checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
