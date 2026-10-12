#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
validator = ROOT / "projects/tests/l08/validate_submission.py"
solution = ROOT / "projects/reference/l08/reference_solution.py"
run = ROOT / "projects/reference/l08/sample-run/adaptation-run.json"

result = subprocess.run(
    [sys.executable, str(validator), str(solution), str(run)],
    text=True,
    capture_output=True,
)
if result.returncode != 0:
    raise SystemExit(result.stdout + result.stderr)
if "PASS: p08-adapt-small-llm objective checks" not in result.stdout:
    raise SystemExit("reference validator did not emit expected PASS marker")

failure = ROOT / "projects/reference/l08/failure-run/adaptation-run.json"
bad = subprocess.run(
    [sys.executable, str(validator), str(solution), str(failure)],
    text=True,
    capture_output=True,
)
if bad.returncode == 0:
    raise SystemExit("intentional p08 failure fixture was accepted")

print("PASS: p08 reference solution satisfies objective validator")
