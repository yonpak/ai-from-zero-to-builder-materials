#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
validator = ROOT / "projects/tests/l10/validate_submission.py"
solution = ROOT / "projects/reference/l10/reference_solution.py"
passing = ROOT / "projects/reference/l10/sample-run/tool-run.json"
failure = ROOT / "projects/reference/l10/failure-run/tool-run.json"

result = subprocess.run([sys.executable, str(validator), str(solution), str(passing)], text=True, capture_output=True)
if result.returncode != 0:
    raise SystemExit(result.stdout + result.stderr)
if "PASS: p10-tool-using-assistant objective checks" not in result.stdout:
    raise SystemExit("reference validator did not emit expected PASS marker")

bad = subprocess.run([sys.executable, str(validator), str(solution), str(failure)], text=True, capture_output=True)
if bad.returncode == 0:
    raise SystemExit("intentional authorization/approval failure was accepted")

print("PASS: p10 reference solution satisfies objective validator")
