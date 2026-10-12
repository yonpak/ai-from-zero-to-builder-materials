#!/usr/bin/env python3
"""Verify the committed p04 reference solution against the objective validator."""

from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
VALIDATOR = ROOT / "projects/tests/l04/validate_submission.py"
REFERENCE = ROOT / "projects/reference/l04/reference_solution.py"

spec = importlib.util.spec_from_file_location("p04_validator", VALIDATOR)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load p04 validator")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

module = validator.load_module(REFERENCE)
validator.validate(module)
print("PASS: p04 reference solution satisfies objective validator")


sys.path.insert(0, str(ROOT / "projects" / "tests"))
from failure_fixture import expect_rejected, mutated_copy

with mutated_copy(
    REFERENCE,
    [
        (
            'ids = [stoi["<bos>"], *body, stoi["<eos>"]]',
            'ids = [stoi["<bos>"], *body, stoi["<eos>"]][:max_length]',
        ),
        ("body = body[: max_length - 2]", "body = body[:max_length]"),
    ],
) as broken:
    expect_rejected(
        [VALIDATOR, broken],
        "p04 truncation can drop the EOS marker",
    )
