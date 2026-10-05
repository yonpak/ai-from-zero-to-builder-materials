#!/usr/bin/env python3
import importlib.util, json, sys
from pathlib import Path

def fail(msg): raise AssertionError(msg)

def load_module(path):
    spec=importlib.util.spec_from_file_location("p13_submission",path)
    if spec is None or spec.loader is None: fail("cannot import submission")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def expect_value_error(fn,msg):
    try: fn()
    except ValueError: return
    fail(msg)

def objective_checks(m,run):
    required=["protocol_compatible","expose_mcp_capabilities","select_agent","artifact_allowed","apply_versioned_update","validate_run"]
    for name in required:
        if not callable(getattr(m,name,None)): fail("missing callable "+name)

    if not m.protocol_compatible("mcp","2026-07-28"): fail("pinned MCP should match")
    if m.protocol_compatible("mcp","2025-11-25"): fail("old MCP version should not match")
    if not m.protocol_compatible("a2a","1.0.0"): fail("pinned A2A should match")
    expect_value_error(lambda:m.protocol_compatible("other","1"),"unknown protocol kind must reject")

    catalog=[
      {"name":"get_order","protocol_version":"2026-07-28"},
      {"name":"refund_order","protocol_version":"2026-07-28"},
      {"name":"old_tool","protocol_version":"2025-11-25"},
    ]
    exposed=m.expose_mcp_capabilities(catalog,"reader",run["policy"])
    if exposed!=["get_order"]: fail(f"unexpected capability exposure: {exposed}")

    cards=[
      {"name":"b","a2a_version":"1.0.0","skills":["logs"],"interfaces":["structured"],"priority":2},
      {"name":"a","a2a_version":"1.0.0","skills":["logs"],"interfaces":["structured"],"priority":1},
      {"name":"old","a2a_version":"0.3.0","skills":["logs"],"interfaces":["structured"],"priority":0},
    ]
    if m.select_agent(cards,"logs","structured")!="a": fail("select_agent must filter version/capability and apply priority")
    if m.select_agent(cards,"travel","structured") is not None: fail("unsupported skill should return None")

    good={"task_id":"task-7","artifact_id":"a1","type":"report"}
    if not m.artifact_allowed(good,"task-7",{"report"}): fail("valid artifact rejected")
    if m.artifact_allowed({**good,"task_id":"other"},"task-7",{"report"}): fail("wrong-task artifact accepted")
    if m.artifact_allowed({**good,"type":"binary"},"task-7",{"report"}): fail("wrong artifact type accepted")

    state={"version":7,"status":"working"}
    updated=m.apply_versioned_update(state,7,{"status":"review"})
    if updated["version"]!=8 or updated["status"]!="review": fail("versioned update failed")
    expect_value_error(lambda:m.apply_versioned_update(updated,7,{"status":"done"}),"stale write must reject")

    m.validate_run(run)

    tampered=json.loads(json.dumps(run))
    tampered["runs"][0]["mcp_version"]="2025-11-25"
    expect_value_error(lambda:m.validate_run(tampered),"run-level protocol mismatch must reject")

    tampered=json.loads(json.dumps(run))
    tampered["runs"][2]["role"]="reader"
    expect_value_error(lambda:m.validate_run(tampered),"unauthorized MCP capability must reject")

    tampered=json.loads(json.dumps(run))
    tampered["runs"][1]["events"][2]["task_id"]="wrong"
    expect_value_error(lambda:m.validate_run(tampered),"wrong-task artifact must reject")

    tampered=json.loads(json.dumps(run))
    tampered["release_passed"]=False
    expect_value_error(lambda:m.validate_run(tampered),"release flag must be recomputed")

def main():
    if len(sys.argv)!=3: raise SystemExit("usage: validate_submission.py SUBMISSION.py SYSTEM-RUN.json")
    module=load_module(Path(sys.argv[1]))
    data=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    objective_checks(module,data)
    print("PASS: p13-interoperable-agent-system objective checks")

if __name__=="__main__": main()
