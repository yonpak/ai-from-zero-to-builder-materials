#!/usr/bin/env python3
"""Learner exercise for L14.12: plan capacity with failure reserve."""

import math


def required_replicas(arrival_rps, safe_rps_per_replica, target_utilization):
    # TODO 1: compute usable per-replica capacity at the target utilization.
    # TODO 2: round required capacity up to a whole replica.
    raise NotImplementedError("TODO: implement capacity calculation")


def survives_one_failure(healthy_replicas, required):
    # TODO 3: check whether one replica can fail while required capacity remains.
    raise NotImplementedError("TODO: implement failure-reserve check")


required = required_replicas(18, 8, 0.8)
assert required == 3
assert survives_one_failure(4, required)
assert not survives_one_failure(3, required)
print("PASS: learner capacity plan includes explicit one-replica failure reserve")
