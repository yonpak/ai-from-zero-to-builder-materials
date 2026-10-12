#!/usr/bin/env python3
"""Verify that the reference solution satisfies the same learner validator."""

from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "projects" / "tests" / "l00" / "validate_submission.py"
REFERENCE = ROOT / "projects" / "reference" / "l00" / "reference_solution.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load(VALIDATOR, "p00_validator")
reference = load(REFERENCE, "p00_reference")
validator.validate(reference)
print("PASS: p00 reference solution satisfies objective validator")


sys.path.insert(0, str(ROOT / "projects" / "tests"))
from failure_fixture import expect_rejected, mutated_copy

with mutated_copy(
    REFERENCE,
    ("return value >= threshold", "return value > threshold"),
) as broken:
    expect_rejected(
        [VALIDATOR, broken],
        "p00 off-by-one threshold boundary",
        marker="predict(4, 4) should be True",
    )
