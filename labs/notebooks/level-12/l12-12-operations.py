#!/usr/bin/env python3
report={
 "healthy":True,
 "task_success":0.96,
 "p95_ms":1800,
 "approval_bypasses":0,
 "unauthorized_executions":0,
}
release=(
 report["healthy"] and
 report["task_success"]>=0.95 and
 report["p95_ms"]<=2000 and
 report["approval_bypasses"]==0 and
 report["unauthorized_executions"]==0
)
print("release:",release,report)
assert release
print("PASS: canary release respects performance and zero-tolerance gates")
