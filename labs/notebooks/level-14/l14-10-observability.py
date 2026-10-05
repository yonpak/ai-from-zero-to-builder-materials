#!/usr/bin/env python3
"""L14.10 local preflight: aggregate metrics with bounded labels; keep per-request IDs in logs and traces."""
events = [
    {"request_id": "r-1001", "deployment": "v2", "status": "ok", "queue_ms": 20, "ttft_ms": 180},
    {"request_id": "r-1002", "deployment": "v2", "status": "ok", "queue_ms": 30, "ttft_ms": 210},
    {"request_id": "r-1003", "deployment": "v2", "status": "error", "queue_ms": 120, "ttft_ms": 0},
]
allowed_metric_labels = {"deployment", "status"}
candidate_labels = {"deployment", "status"}  # try adding "request_id"

rejected = sorted(candidate_labels - allowed_metric_labels)
print("candidate metric labels:", sorted(candidate_labels))
if rejected:
    values = len({e[rejected[0]] for e in events})
    print(f"REJECT: label {rejected[0]!r} is unbounded ({values} values from {len(events)} events; one new series per request)")
    print("keep it in logs and traces instead")
    raise SystemExit(1)
metrics = {
    "requests": len(events),
    "errors": sum(e["status"] == "error" for e in events),
    "avg_queue_ms": round(sum(e["queue_ms"] for e in events) / len(events), 1),
}
print(metrics)

print("PASS: aggregate metrics use bounded labels and preserve deployment evidence")
