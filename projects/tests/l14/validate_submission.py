#!/usr/bin/env python3
import importlib.util, json, sys
from pathlib import Path

def fail(msg): raise AssertionError(msg)

def load_module(path):
    spec=importlib.util.spec_from_file_location("p14_submission",path)
    if spec is None or spec.loader is None: fail("cannot import submission")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def expect_value_error(fn,msg):
    try: fn()
    except ValueError: return
    fail(msg)

def objective_checks(m,run):
    required=["validate_request","batch_requests","memory_admit","deployment_identity","aggregate_metrics","rollout_allowed","required_replicas","validate_run"]
    for name in required:
        if not callable(getattr(m,name,None)): fail("missing callable "+name)

    policy=run["policy"]
    if not m.validate_request({"input":"hi","max_tokens":32},policy): fail("valid request rejected")
    if m.validate_request({"input":"","max_tokens":32},policy): fail("blank input accepted")
    if m.validate_request({"input":"hi","max_tokens":4096},policy): fail("oversized output accepted")

    reqs=[{"id":"a","arrival_ms":0},{"id":"b","arrival_ms":3},{"id":"c","arrival_ms":20}]
    if m.batch_requests(reqs,2,10)!=[["a","b"],["c"]]: fail("batching contract failed")

    if not m.memory_admit(4,8,2): fail("safe memory rejected")
    if m.memory_admit(7,8,2): fail("reserve-violating memory accepted")
    expect_value_error(lambda:m.memory_admit(-1,8,2),"negative memory must reject")

    dep=run["deployments"][0]
    ident=m.deployment_identity(dep)
    if ident[0]!=dep["image_digest"] or ident[2]!=dep["model_revision"]: fail("deployment identity contract failed")

    metrics={
      "task_success":1.0,
      "invalid_requests_executed":0,
      "memory_admission_violations":0,
      "deployment_identity_mismatches":0,
      "critical_violations":0,
      "p95_ttft_ms":250,
    }
    if not m.rollout_allowed(metrics,run["release_rule"]): fail("valid rollout rejected")
    if m.required_replicas(18,8,.8)!=3: fail("capacity calculation failed")

    m.validate_run(run)

    tampered=json.loads(json.dumps(run)); tampered["runs"][0]["request"]["max_tokens"]=4096
    expect_value_error(lambda:m.validate_run(tampered),"invalid executed request must reject")

    tampered=json.loads(json.dumps(run)); tampered["runs"][1]["estimated_memory_gb"]=7.0
    expect_value_error(lambda:m.validate_run(tampered),"unsafe admission must reject")

    tampered=json.loads(json.dumps(run)); tampered["runs"][2]["image_digest"]="sha256:wrong"
    expect_value_error(lambda:m.validate_run(tampered),"deployment mismatch must reject")

    tampered=json.loads(json.dumps(run)); tampered["release_passed"]=False
    expect_value_error(lambda:m.validate_run(tampered),"release flag must be recomputed")

def main():
    if len(sys.argv)!=3: raise SystemExit("usage: validate_submission.py SUBMISSION.py SERVICE-RUN.json")
    module=load_module(Path(sys.argv[1]))
    data=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    objective_checks(module,data)
    print("PASS: p14-production-ai-service objective checks")

if __name__=="__main__": main()
