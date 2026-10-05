def earliest_failure(trace):
    checks = [
        ("goal_drift", trace.get("goal_aligned", True)),
        ("stale_state", trace.get("state_current", True)),
        ("tool_selection", trace.get("selection_correct", True)),
        ("memory_contamination", trace.get("memory_scope_ok", True)),
        ("authority", trace.get("authority_ok", True)),
        ("stopping", trace.get("stopping_ok", True)),
    ]
    for name, ok in checks:
        if not ok:
            return name
    return "none"

traces = [
    {"id": "stale", "state_current": False, "selection_correct": False},
    {"id": "selection", "selection_correct": False},
    {"id": "authority", "authority_ok": False},
    {"id": "clean"},
]
for trace in traces:
    print(trace["id"], "=>", earliest_failure(trace))
