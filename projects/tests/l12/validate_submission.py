#!/usr/bin/env python3
import importlib.util, json, sys
from pathlib import Path

def fail(msg): raise AssertionError(msg)

def load_module(path):
    spec=importlib.util.spec_from_file_location("p12_submission",path)
    if spec is None or spec.loader is None: fail("cannot import submission")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def expect_value_error(fn,msg):
    try: fn()
    except ValueError: return
    fail(msg)

def objective_checks(m,run):
    required=["claim_task","operation_key","retry_decision","authorize","sandbox_allows","retrieve_memory","schedule_waves","validate_delegation","validate_run"]
    for name in required:
        if not callable(getattr(m,name,None)): fail("missing callable "+name)

    task={"task_id":"T1","owner":None,"lease_until":0,"state":"QUEUED"}
    claimed=m.claim_task(task,"worker-a",0,2)
    if claimed["task_id"]!="T1" or claimed["owner"]!="worker-a" or claimed["state"]!="RUNNING": fail("claim_task contract failed")
    expect_value_error(lambda:m.claim_task({"task_id":"T1","owner":"a","lease_until":5},"b",2,2),"active lease must reject second claimant")

    a=m.operation_key("T1","refund_order",{"amount":20,"order_id":"4172"})
    b=m.operation_key("T1","refund_order",{"order_id":"4172","amount":20})
    if a!=b or not a: fail("operation_key must be stable across argument ordering")
    if m.operation_key("T2","refund_order",{"amount":20,"order_id":"4172"})==a: fail("task identity must affect operation key")

    if not m.retry_decision("timeout",1,2)["retry"]: fail("timeout should retry within budget")
    if m.retry_decision("permission_denied",1,2)["retry"]: fail("permission denial must not retry")
    if m.retry_decision("timeout",3,2)["retry"]: fail("retry budget must stop later attempt")

    policy=run["policy"]
    if not m.authorize("reader","get_order",policy): fail("reader should read")
    if m.authorize("reader","refund_order",policy): fail("reader should not refund")
    if not m.authorize("reader","ask_user",policy): fail("control action should be allowed")

    profile={"write_root":"/workspace/task","network_hosts":["inventory.internal"],"max_memory_mb":256}
    good={"path":"/workspace/task/report.txt","host":"inventory.internal","memory_mb":128}
    if not m.sandbox_allows(good,profile): fail("valid sandbox request rejected")
    if m.sandbox_allows({**good,"path":"/home/user/.ssh/id_rsa"},profile): fail("outside path accepted")
    if m.sandbox_allows({**good,"host":"public.example"},profile): fail("outside host accepted")

    memory=[
      {"id":"good","scope":"u7","source":"profile","age_days":2,"relevance":0.8},
      {"id":"guess","scope":"u7","source":"model_guess","age_days":1,"relevance":1.0},
      {"id":"other","scope":"u8","source":"profile","age_days":0,"relevance":1.0},
    ]
    got=m.retrieve_memory(memory,"u7",{"trusted_sources":["profile"],"max_age_days":30},2)
    if [x["id"] for x in got]!=["good"]: fail("memory policy failed")

    waves=m.schedule_waves({"a":set(),"b":set(),"c":{"a","b"}},2)
    if waves!=[["a","b"],["c"]]: fail(f"unexpected waves {waves}")
    expect_value_error(lambda:m.schedule_waves({"a":{"b"},"b":{"a"}},2),"cycle must reject")

    env={"subgoal":"inspect logs","allowed_tools":["read_logs"],"step_budget":2,"expected_fields":["evidence","request_id"]}
    if not m.validate_delegation(env,{"read_logs","refund_order"},4): fail("valid delegation rejected")
    if m.validate_delegation({**env,"allowed_tools":["refund_order"]},{"read_logs"},4): fail("tool escalation accepted")

    m.validate_run(run)

    tampered=json.loads(json.dumps(run))
    tampered["traces"][0]["principal_role"]="reader"
    tampered["traces"][0]["steps"][0]["action"]="refund_order"
    tampered["traces"][0]["steps"][0]["side_effect"]=True
    tampered["traces"][0]["steps"][0]["operation_id"]="bad"
    expect_value_error(lambda:m.validate_run(tampered),"unauthorized side effect must reject")

    tampered=json.loads(json.dumps(run))
    tampered["traces"][1]["steps"][1]["reconciled"]=False
    expect_value_error(lambda:m.validate_run(tampered),"duplicate side effect must reject")

    tampered=json.loads(json.dumps(run))
    tampered["release_passed"]=False
    expect_value_error(lambda:m.validate_run(tampered),"release flag must be recomputed")

def main():
    if len(sys.argv)!=3: raise SystemExit("usage: validate_submission.py SUBMISSION.py HARNESS-RUN.json")
    module=load_module(Path(sys.argv[1]))
    data=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    objective_checks(module,data)
    print("PASS: p12-agent-harness objective checks")

if __name__=="__main__": main()
