#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
VALIDATOR=HERE/"validate_submission.py"
REFERENCE=REPO/"projects"/"reference"/"l14"/"reference_solution.py"
PASSING=REPO/"projects"/"reference"/"l14"/"sample-run"/"service-run.json"
FAILURE=REPO/"projects"/"reference"/"l14"/"failure-run"/"service-run.json"
p=subprocess.run([sys.executable,str(VALIDATOR),str(REFERENCE),str(PASSING)],cwd=REPO,text=True,capture_output=True)
if p.returncode!=0:
    raise SystemExit("FAIL: p14 reference did not pass objective validator\n"+p.stdout+p.stderr)
if "PASS: p14-production-ai-service objective checks" not in p.stdout:
    raise SystemExit("FAIL: expected p14 success marker missing")
f=subprocess.run([sys.executable,str(VALIDATOR),str(REFERENCE),str(FAILURE)],cwd=REPO,text=True,capture_output=True)
if f.returncode==0:
    raise SystemExit("FAIL: p14 intentional failure fixture unexpectedly passed")
print("PASS: p14 reference solution satisfies objective validator")
