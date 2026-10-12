#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
validator = ROOT / "projects/tests/l09/validate_submission.py"
solution = ROOT / "projects/reference/l09/reference_solution.py"
passing = ROOT / "projects/reference/l09/sample-run/rag-run.json"
failure = ROOT / "projects/reference/l09/failure-run/rag-run.json"

result = subprocess.run(
    [sys.executable, str(validator), str(solution), str(passing)],
    text=True,
    capture_output=True,
)
if result.returncode != 0:
    raise SystemExit(result.stdout + result.stderr)
if "PASS: p09-evidence-rag objective checks" not in result.stdout:
    raise SystemExit("reference validator did not emit expected PASS marker")

bad = subprocess.run(
    [sys.executable, str(validator), str(solution), str(failure)],
    text=True,
    capture_output=True,
)
if bad.returncode == 0:
    raise SystemExit("intentional cross-tenant failure was accepted")

print("PASS: p09 reference solution satisfies objective validator")
