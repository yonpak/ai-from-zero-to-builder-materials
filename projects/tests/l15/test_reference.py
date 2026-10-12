#!/usr/bin/env python3
"""Self-test the deterministic Level 15 release validator and optional product contract."""

import runpy
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
VALIDATOR = HERE / "validate_submission.py"
PRODUCT_VALIDATOR = HERE / "validate_product.py"
PRODUCT_FIXTURE = HERE / "product_contract_fixture.py"
REAL_RAG_RUNTIME_TEST = HERE / "test_real_rag_runtime.py"
STARTER_PRODUCT = REPO / "projects" / "starters" / "l15" / "product.py"
REFERENCE = REPO / "projects" / "reference" / "l15" / "reference_solution.py"
PASSING = REPO / "projects" / "reference" / "l15" / "sample-run" / "capstone-run.json"
FAILURE = REPO / "projects" / "reference" / "l15" / "failure-run" / "capstone-run.json"

reference_namespace = runpy.run_path(str(REFERENCE))
valid_reproduction = {
    "claim": "candidate improves score",
    "environment": {"python": "3.11", "platform": "cpu"},
    "seed_policy": "fixed seed 13",
    "baseline": 0.72,
    "candidate": 0.78,
    "expected_relation": "candidate_gt_baseline",
    "conclusion": "confirmed_in_scope",
}
if not reference_namespace["reproduction_record_valid"](valid_reproduction):
    raise SystemExit("FAIL: valid reproduction evidence was rejected")

invalid_numeric_values = [
    ("baseline", False),
    ("candidate", True),
    ("baseline", float("nan")),
    ("candidate", float("inf")),
    ("candidate", float("-inf")),
]
for field, value in invalid_numeric_values:
    record = dict(valid_reproduction)
    record[field] = value
    if reference_namespace["reproduction_record_valid"](record):
        raise SystemExit(
            f"FAIL: reference accepted invalid reproduction numeric {field}={value!r}"
        )

large_integer_record = dict(valid_reproduction)
large_integer_record["candidate"] = 10**1000
if not reference_namespace["reproduction_record_valid"](large_integer_record):
    raise SystemExit("FAIL: reference rejected a finite large reproduction integer")


passing = subprocess.run(
    [sys.executable, str(VALIDATOR), str(REFERENCE), str(PASSING)],
    cwd=REPO,
    text=True,
    capture_output=True,
)
if passing.returncode != 0:
    raise SystemExit(
        "FAIL: p15 reference did not pass objective validator\n"
        + passing.stdout
        + passing.stderr
    )
if "PASS: p15-ai-product-capstone objective checks" not in passing.stdout:
    raise SystemExit("FAIL: expected p15 success marker missing")

failure = subprocess.run(
    [sys.executable, str(VALIDATOR), str(REFERENCE), str(FAILURE)],
    cwd=REPO,
    text=True,
    capture_output=True,
)
if failure.returncode == 0:
    raise SystemExit("FAIL: p15 intentional failure fixture unexpectedly passed")

product = subprocess.run(
    [sys.executable, str(PRODUCT_VALIDATOR), str(PRODUCT_FIXTURE)],
    cwd=REPO,
    text=True,
    capture_output=True,
)
if product.returncode != 0:
    raise SystemExit(
        "FAIL: p15 product contract checker rejected its deterministic fixture\n"
        + product.stdout
        + product.stderr
    )
if "PASS: Level 15 RAG product contract checks" not in product.stdout:
    raise SystemExit("FAIL: expected p15 product-contract success marker missing")

real_rag_runtime = subprocess.run(
    [sys.executable, str(REAL_RAG_RUNTIME_TEST)],
    cwd=REPO,
    text=True,
    capture_output=True,
)
if real_rag_runtime.returncode != 0:
    raise SystemExit(
        "FAIL: Level 15 real-RAG runtime regression checks failed\n"
        + real_rag_runtime.stdout
        + real_rag_runtime.stderr
    )
if "PASS: Level 15 real-RAG runtime success and failure-path checks" not in real_rag_runtime.stdout:
    raise SystemExit("FAIL: expected real-RAG runtime success marker missing")

unfinished_product = subprocess.run(
    [sys.executable, str(PRODUCT_VALIDATOR), str(STARTER_PRODUCT)],
    cwd=REPO,
    text=True,
    capture_output=True,
)
if unfinished_product.returncode == 0:
    raise SystemExit("FAIL: unfinished p15 learner product unexpectedly passed contract checks")

print("PASS: p15 reference solution satisfies objective validator")
print("PASS: p15 product contract checker satisfies deterministic fixture")
print("PASS: p15 real-RAG runtime preserves stage evidence")
