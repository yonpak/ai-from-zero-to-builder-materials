#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
validator = ROOT / "projects/tests/l07/validate_submission.py"
solution = ROOT / "projects/reference/l07/reference_solution.py"
run = ROOT / "projects/reference/l07/sample-run/workflow-run.json"

result = subprocess.run(
    [sys.executable, str(validator), str(solution), str(run)],
    text=True,
    capture_output=True,
)
if result.returncode != 0:
    raise SystemExit(result.stdout + result.stderr)
if "PASS: p07-reliable-llm-workflow objective checks" not in result.stdout:
    raise SystemExit("reference validator did not emit expected PASS marker")

failure = ROOT / "projects/reference/l07/failure-run/workflow-run.json"
bad = subprocess.run(
    [sys.executable, str(validator), str(solution), str(failure)],
    text=True,
    capture_output=True,
)
if bad.returncode == 0:
    raise SystemExit("intentional provenance failure was accepted")

print("PASS: p07 reference solution satisfies objective validator")
