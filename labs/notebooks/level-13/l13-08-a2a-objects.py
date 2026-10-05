#!/usr/bin/env python3
"""L13.8 local Lab: every message, status update, and artifact must name the same task."""
events = [
    {"type": "message", "context_id": "ctx-1", "task_id": "task-7", "role": "user"},
    {"type": "task_status", "context_id": "ctx-1", "task_id": "task-7", "state": "working"},
    {"type": "artifact", "context_id": "ctx-1", "task_id": "task-7", "artifact_id": "report-1"},
    {"type": "task_status", "context_id": "ctx-1", "task_id": "task-7", "state": "completed"},
]
task_id = "task-7"
bad = []
for e in events:
    ok = e["task_id"] == task_id and e["context_id"] == "ctx-1"
    print(f"{'ok  ' if ok else 'FAIL'} {e['type']:12s} task_id={e['task_id']}")
    if not ok:
        bad.append(e)
if bad:
    print("REJECT: provenance broken; an object claims a different task than the one we are tracking")
    raise SystemExit(1)
artifact = [e for e in events if e["type"] == "artifact"][0]
print("artifact provenance:", artifact["task_id"], artifact["artifact_id"])
print("PASS: message, task status, and artifact keep explicit task identity")
