#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
VALIDATOR=HERE/"validate_submission.py"
REFERENCE=REPO/"projects"/"reference"/"l13"/"reference_solution.py"
PASSING=REPO/"projects"/"reference"/"l13"/"sample-run"/"system-run.json"
FAILURE=REPO/"projects"/"reference"/"l13"/"failure-run"/"system-run.json"
p=subprocess.run([sys.executable,str(VALIDATOR),str(REFERENCE),str(PASSING)],cwd=REPO,text=True,capture_output=True)
if p.returncode!=0:
    raise SystemExit("FAIL: p13 reference did not pass objective validator\n"+p.stdout+p.stderr)
if "PASS: p13-interoperable-agent-system objective checks" not in p.stdout:
    raise SystemExit("FAIL: expected p13 success marker missing")
f=subprocess.run([sys.executable,str(VALIDATOR),str(REFERENCE),str(FAILURE)],cwd=REPO,text=True,capture_output=True)
if f.returncode==0:
    raise SystemExit("FAIL: p13 intentional failure fixture unexpectedly passed")
print("PASS: p13 reference solution satisfies objective validator")
