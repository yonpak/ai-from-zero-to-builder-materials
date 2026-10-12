#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
VALIDATOR = HERE / "validate_submission.py"
REFERENCE = REPO / "projects" / "reference" / "l11" / "reference_solution.py"
PASSING = REPO / "projects" / "reference" / "l11" / "sample-run" / "agent-run.json"
FAILURE = REPO / "projects" / "reference" / "l11" / "failure-run" / "agent-run.json"

passed = subprocess.run(
    [sys.executable, str(VALIDATOR), str(REFERENCE), str(PASSING)],
    cwd=REPO,
    text=True,
    capture_output=True,
)
if passed.returncode != 0:
    raise SystemExit(
        "FAIL: p11 reference did not pass objective validator\n"
        + passed.stdout
        + passed.stderr
    )
if "PASS: p11-bounded-agent objective checks" not in passed.stdout:
    raise SystemExit("FAIL: p11 passing reference did not emit expected marker")

failed = subprocess.run(
    [sys.executable, str(VALIDATOR), str(REFERENCE), str(FAILURE)],
    cwd=REPO,
    text=True,
    capture_output=True,
)
if failed.returncode == 0:
    raise SystemExit("FAIL: p11 intentional failure fixture unexpectedly passed")

print("PASS: p11 reference solution satisfies objective validator")
