#!/usr/bin/env python3
import json, sys
from pathlib import Path

def fail(msg): raise SystemExit("FAIL: "+msg)

def recompute(data):
    invalid=0; admission_violations=0; deployment_mismatches=0; critical=0; success=0; ttfts=[]
    deployments={d["id"]:d for d in data["deployments"]}
    for run in data["runs"]:
        success+=int(run["observed_terminal"]==run["expected_terminal"])
        ttfts.append(run["ttft_ms"])
        dep=deployments.get(run["deployment_id"])
        if dep is None or dep["image_digest"]!=run["image_digest"] or dep["model_revision"]!=run["model_revision"]:
            deployment_mismatches+=1
        req=run["request"]
        valid=(isinstance(req.get("input"),str) and bool(req["input"].strip())
               and isinstance(req.get("max_tokens"),int)
               and 1<=req["max_tokens"]<=data["policy"]["max_tokens"])
        if run.get("executed") and not valid:
            invalid+=1
        if run.get("admitted") and run["estimated_memory_gb"]>run["available_memory_gb"]:
            admission_violations+=1
        critical+=int(run.get("critical_violation",False))
    ordered=sorted(ttfts)
    return {
      "task_success":success/len(data["runs"]),
      "invalid_requests_executed":invalid,
      "memory_admission_violations":admission_violations,
      "deployment_identity_mismatches":deployment_mismatches,
      "critical_violations":critical,
      "p95_ttft_ms":ordered[max(0,int(.95*len(ordered))-1)],
    }

def validate(data):
    got=recompute(data)
    if got!=data["metrics"]: fail(f"metrics mismatch: expected {got!r}")
    r=data["release_rule"]
    release=(got["task_success"]>=r["min_task_success"]
             and got["invalid_requests_executed"]<=r["max_invalid_requests_executed"]
             and got["memory_admission_violations"]<=r["max_memory_admission_violations"]
             and got["deployment_identity_mismatches"]<=r["max_deployment_identity_mismatches"]
             and got["critical_violations"]<=r["max_critical_violations"]
             and got["p95_ttft_ms"]<=r["max_p95_ttft_ms"])
    if data["release_passed"] is not release: fail("release_passed mismatch")
    if not release: fail("release rule failed")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: l14-13-integration-check.py SERVICE-RUN.json")
    validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print("PASS: Level 14 integration trace")
