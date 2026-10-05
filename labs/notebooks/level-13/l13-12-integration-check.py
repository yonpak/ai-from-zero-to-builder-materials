#!/usr/bin/env python3
import json, sys
from pathlib import Path

MCP="2026-07-28"
A2A="1.0.0"

def fail(msg): raise SystemExit("FAIL: "+msg)

def recompute(data):
    unauthorized=0; wrong_artifacts=0; version_mismatches=0; conflicts=0; success=0; messages=0
    for run in data["runs"]:
        if run["mcp_version"]!=MCP: version_mismatches+=1
        if run["a2a_version"]!=A2A: version_mismatches+=1
        success+=int(run["observed_terminal"]==run["expected_terminal"])
        role=run["role"]
        allowed=set(data["policy"]["roles"].get(role,[]))|set(data["policy"].get("control_actions",[]))
        for event in run["events"]:
            messages+=int(event.get("kind") in {"message","task_status"})
            if event.get("kind")=="mcp_call" and event.get("executed") and event.get("capability") not in allowed:
                unauthorized+=1
            if event.get("kind")=="artifact" and event.get("task_id")!=run.get("child_task_id"):
                wrong_artifacts+=1
            if event.get("kind")=="state_write" and event.get("expected_version")!=event.get("observed_version"):
                conflicts+=1
    return {
      "task_success":success/len(data["runs"]),
      "protocol_version_mismatches":version_mismatches,
      "unauthorized_capability_calls":unauthorized,
      "wrong_task_artifacts":wrong_artifacts,
      "state_conflicts":conflicts,
      "message_count":messages,
    }

def validate(data):
    got=recompute(data)
    if got!=data["metrics"]: fail(f"metrics mismatch: expected {got!r}")
    r=data["release_rule"]
    release=(got["task_success"]>=r["min_task_success"]
      and got["protocol_version_mismatches"]<=r["max_protocol_version_mismatches"]
      and got["unauthorized_capability_calls"]<=r["max_unauthorized_capability_calls"]
      and got["wrong_task_artifacts"]<=r["max_wrong_task_artifacts"]
      and got["state_conflicts"]<=r["max_state_conflicts"])
    if data["release_passed"] is not release: fail("release_passed mismatch")
    if not release: fail("release rule failed")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: l13-12-integration-check.py SYSTEM-RUN.json")
    validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print("PASS: Level 13 integration trace")
