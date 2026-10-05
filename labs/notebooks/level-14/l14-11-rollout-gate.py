#!/usr/bin/env python3
"""L14.11 local preflight: a canary is promoted only if every predefined gate passes."""
canary = {"error_rate": 0.015, "p95_ms": 980, "critical_violations": 0}
rule = {"max_error_rate": 0.02, "max_p95_ms": 1100, "max_critical_violations": 0}
gates = {
    "error_rate": canary["error_rate"] <= rule["max_error_rate"],
    "p95_ms": canary["p95_ms"] <= rule["max_p95_ms"],
    "critical_violations": canary["critical_violations"] <= rule["max_critical_violations"],
}
for name, ok in gates.items():
    limit = rule["max_" + name]
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {canary[name]} (limit {limit})")
release = all(gates.values())
print("decision:", "promote canary" if release else "roll back canary")
if not release:
    raise SystemExit(1)
print("PASS: canary release is controlled by predefined gates")
