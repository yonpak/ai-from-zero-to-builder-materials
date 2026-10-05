#!/usr/bin/env python3
import json, sys
from pathlib import Path

def fail(msg): raise SystemExit("FAIL: "+msg)

def metrics(data):
    policy=data["policy"]
    seen_ops=set(); duplicate=0; unauthorized=0; recovered=0; successes=0; total_cost=0.0; latencies=[]
    for trace in data["traces"]:
        successes+=int(trace["observed_terminal"]==trace["expected_terminal"])
        latencies.append(trace["latency_ms"])
        total_cost+=trace["cost_units"]
        for step in trace["steps"]:
            action=step["action"]; role=trace["principal_role"]
            allowed=set(policy["roles"].get(role,[]))|set(policy.get("control_actions",[]))
            if step.get("executed") and action not in allowed:
                unauthorized+=1
            op=step.get("operation_id")
            if step.get("side_effect") and step.get("executed") and op:
                if op in seen_ops and not step.get("reconciled",False):
                    duplicate+=1
                seen_ops.add(op)
            if step.get("recovered"):
                recovered+=1
    return {
      "task_success":successes/len(data["traces"]),
      "unauthorized_executions":unauthorized,
      "duplicate_side_effects":duplicate,
      "recovered_failures":recovered,
      "p95_latency_ms":sorted(latencies)[max(0,int(.95*len(latencies))-1)],
      "total_cost_units":round(total_cost,3),
    }

def validate(data):
    got=metrics(data)
    if got!=data["metrics"]:
        fail(f"metrics mismatch: expected {got!r}")
    rule=data["release_rule"]
    release=(got["task_success"]>=rule["min_task_success"] and
             got["unauthorized_executions"]<=rule["max_unauthorized_executions"] and
             got["duplicate_side_effects"]<=rule["max_duplicate_side_effects"] and
             got["p95_latency_ms"]<=rule["max_p95_latency_ms"] and
             got["total_cost_units"]<=rule["max_total_cost_units"])
    if data["release_passed"] is not release:
        fail("release_passed mismatch")
    if not release:
        fail("release rule failed")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: l12-13-integration-check.py HARNESS-RUN.json")
    validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print("PASS: Level 12 integration trace")
