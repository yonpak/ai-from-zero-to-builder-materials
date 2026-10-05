#!/usr/bin/env python3
"""L13.11 local preflight: recompute coordination metrics from raw traces."""
AGENT_SKILLS = {"log-agent": {"log_analysis"}, "policy-agent": {"policy_lookup"}, "travel-agent": {"itinerary"}}

traces = [
    {"id": "t1", "needs": "log_analysis", "assigned": "log-agent", "success": True, "handoff_ok": True, "unauthorized": 0, "messages": 3},
    {"id": "t2", "needs": "policy_lookup", "assigned": "policy-agent", "success": True, "handoff_ok": True, "unauthorized": 0, "messages": 4},
    {"id": "t3", "needs": "log_analysis", "assigned": "travel-agent", "success": False, "handoff_ok": True, "unauthorized": 0, "messages": 2},
]
for t in traces:
    t["route_ok"] = t["needs"] in AGENT_SKILLS[t["assigned"]]  # recomputed, not copied from the trace
    print(f"{t['id']}: needs {t['needs']:13s} -> {t['assigned']:12s} route_ok={t['route_ok']}")

n = len(traces)
metrics = {
    "task_success": round(sum(t["success"] for t in traces) / n, 2),
    "routing_accuracy": round(sum(t["route_ok"] for t in traces) / n, 2),
    "handoff_completeness": round(sum(t["handoff_ok"] for t in traces) / n, 2),
    "unauthorized_calls": sum(t["unauthorized"] for t in traces),
    "message_count": sum(t["messages"] for t in traces),
}
print(metrics)
assert metrics["unauthorized_calls"] == 0
print("PASS: evaluation includes coordination metrics")
