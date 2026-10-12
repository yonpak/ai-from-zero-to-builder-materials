#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
validator = ROOT / "projects/tests/l06/validate_submission.py"
solution = ROOT / "projects/reference/l06/reference_solution.py"
run = ROOT / "projects/reference/l06/sample-run/run.json"
result = subprocess.run([sys.executable, str(validator), str(solution), str(run)], text=True, capture_output=True)
if result.returncode != 0:
    raise SystemExit(result.stdout + result.stderr)
if "PASS: p06-tiny-llm objective checks" not in result.stdout:
    raise SystemExit("reference validator did not emit expected PASS marker")
print("PASS: p06 reference solution satisfies objective validator")


sys.path.insert(0, str(ROOT / "projects" / "tests"))
from failure_fixture import expect_rejected

failure = ROOT / "projects/reference/l06/failure-run/run.json"
expect_rejected(
    [validator, solution, failure],
    "p06 tokenizer/checkpoint identity mismatch",
    marker="checkpoint/tokenizer fingerprint mismatch",
)
