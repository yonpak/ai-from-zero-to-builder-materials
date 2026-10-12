#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
VALIDATOR=HERE/"validate_submission.py"
REFERENCE=REPO/"projects"/"reference"/"l12"/"reference_solution.py"
PASSING=REPO/"projects"/"reference"/"l12"/"sample-run"/"harness-run.json"
FAILURE=REPO/"projects"/"reference"/"l12"/"failure-run"/"harness-run.json"
passed=subprocess.run([sys.executable,str(VALIDATOR),str(REFERENCE),str(PASSING)],cwd=REPO,text=True,capture_output=True)
if passed.returncode!=0:
    raise SystemExit("FAIL: p12 reference did not pass objective validator\n"+passed.stdout+passed.stderr)
if "PASS: p12-agent-harness objective checks" not in passed.stdout:
    raise SystemExit("FAIL: expected p12 success marker missing")
failed=subprocess.run([sys.executable,str(VALIDATOR),str(REFERENCE),str(FAILURE)],cwd=REPO,text=True,capture_output=True)
if failed.returncode==0:
    raise SystemExit("FAIL: p12 intentional failure fixture unexpectedly passed")
print("PASS: p12 reference solution satisfies objective validator")
