#!/usr/bin/env python3
"""Learner exercise for L13.10: reject stale shared-state writes."""


def apply_write(state, expected_version, patch):
    # TODO 1: compare expected_version with the current version.
    # TODO 2: reject stale writes without mutating state.
    # TODO 3: apply an accepted patch and increment the version.
    raise NotImplementedError("TODO: implement optimistic concurrency")


state = {"version": 7, "status": "working", "evidence": []}
ok, state = apply_write(state, 7, {"status": "review"})
assert ok and state["version"] == 8 and state["status"] == "review"
ok, stale_state = apply_write(state, 7, {"status": "completed"})
assert not ok and stale_state == state
ok, state = apply_write(state, 8, {"status": "completed"})
assert ok and state["version"] == 9
print("PASS: learner shared-state writer rejects stale versions")
