#!/usr/bin/env python3
"""Learner exercise for L14.11: implement a canary release gate."""


def release_allowed(canary, rule):
    # TODO 1: compare error rate against its maximum.
    # TODO 2: compare p95 latency against its maximum.
    # TODO 3: enforce the zero-tolerance critical-violation gate independently.
    raise NotImplementedError("TODO: implement release gate")


rule = {"max_error_rate": 0.02, "max_p95_ms": 1100, "max_critical_violations": 0}
good = {"error_rate": 0.015, "p95_ms": 980, "critical_violations": 0}
bad_error = {**good, "error_rate": 0.03}
bad_critical = {**good, "critical_violations": 1}
assert release_allowed(good, rule)
assert not release_allowed(bad_error, rule)
assert not release_allowed(bad_critical, rule)
print("PASS: learner rollout gate enforces performance and critical controls")
