#!/usr/bin/env python3
"""Reference answer for L14.12."""

import math


def required_replicas(arrival_rps, safe_rps_per_replica, target_utilization):
    usable = safe_rps_per_replica * target_utilization
    if usable <= 0:
        raise ValueError("usable per-replica capacity must be positive")
    return math.ceil(arrival_rps / usable)


def survives_one_failure(healthy_replicas, required):
    return healthy_replicas - 1 >= required


required = required_replicas(18, 8, 0.8)
assert required == 3
assert required_replicas(6.4, 8, 0.8) == 1
assert survives_one_failure(4, required)
assert not survives_one_failure(3, required)
try:
    required_replicas(10, 8, 0)
except ValueError:
    pass
else:
    raise AssertionError("zero usable capacity must be rejected")
print("PASS: L14.12 reference answer computes capacity and one-replica failure reserve")
