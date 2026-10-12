#!/usr/bin/env python3
"""Reference answer for L14.11."""


def release_allowed(canary, rule):
    return (
        canary["error_rate"] <= rule["max_error_rate"]
        and canary["p95_ms"] <= rule["max_p95_ms"]
        and canary["critical_violations"] <= rule["max_critical_violations"]
    )


rule = {"max_error_rate": 0.02, "max_p95_ms": 1100, "max_critical_violations": 0}
good = {"error_rate": 0.015, "p95_ms": 980, "critical_violations": 0}
assert release_allowed(good, rule)
assert release_allowed({**good, "error_rate": 0.02, "p95_ms": 1100}, rule)
assert not release_allowed({**good, "error_rate": 0.021}, rule)
assert not release_allowed({**good, "p95_ms": 1101}, rule)
assert not release_allowed({**good, "critical_violations": 1}, rule)
print("PASS: L14.11 reference answer enforces error, latency, and critical-violation gates")
