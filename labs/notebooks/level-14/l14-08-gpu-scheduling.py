#!/usr/bin/env python3
"""L14.8 local preflight: place a request only on a replica that is ready and has room for it."""
replicas = [
    {"id": "gpu-a", "ready": True, "headroom_gb": 2.0, "queue": 1},
    {"id": "gpu-b", "ready": True, "headroom_gb": 8.0, "queue": 4},
]
request = {"cache_gb": 5.0}

feasible = []
for r in replicas:
    if not r["ready"]:
        why = "not ready"
    elif r["headroom_gb"] < request["cache_gb"]:
        why = f"only {r['headroom_gb']} GB free, needs {request['cache_gb']} GB"
    else:
        why = "feasible"
        feasible.append(r)
    print(f"{r['id']}: queue={r['queue']} -> {why}")
selected = min(feasible, key=lambda r: r["queue"]) if feasible else None
print("selected:", selected["id"] if selected else None)
if selected is None:
    print("WAIT: no replica can hold this request; keep it queued or shed load")
assert selected is None or selected["headroom_gb"] >= request["cache_gb"]
print("PASS: scheduler checks feasibility before queue preference")
