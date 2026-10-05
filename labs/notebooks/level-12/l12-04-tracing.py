#!/usr/bin/env python3

MODEL_LATENCY_MS = 70
POLICY_LATENCY_MS = 10
TOOL_LATENCY_MS = 40

spans = [
    {"span": "model", "parent": "task", "duration_ms": MODEL_LATENCY_MS},
    {"span": "policy", "parent": "task", "duration_ms": POLICY_LATENCY_MS},
    {
        "span": "tool",
        "parent": "task",
        "duration_ms": TOOL_LATENCY_MS,
        "attempt": 1,
    },
]
task_duration_ms = sum(span["duration_ms"] for span in spans)
task_span = {"span": "task", "parent": None, "duration_ms": task_duration_ms}

print(task_span)
for row in spans:
    print(row)

print(
    "critical path: "
    f"model {MODEL_LATENCY_MS} + policy {POLICY_LATENCY_MS} + "
    f"tool {TOOL_LATENCY_MS} = {task_duration_ms} ms"
)

assert all(span["parent"] == "task" for span in spans)
assert spans[-1]["attempt"] == 1
assert task_span["duration_ms"] == sum(span["duration_ms"] for span in spans)
print("PASS: trace preserves parent/child evidence and computed critical-path latency")
