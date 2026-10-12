#!/usr/bin/env python3
"""Reference answer for L13.10."""


def apply_write(state, expected_version, patch):
    if expected_version != state["version"]:
        return False, state
    next_state = {**state, **patch, "version": state["version"] + 1}
    return True, next_state


state = {"version": 7, "status": "working", "evidence": []}
ok, state = apply_write(state, 7, {"status": "review"})
assert ok and state == {"version": 8, "status": "review", "evidence": []}
before_stale = dict(state)
ok, stale = apply_write(state, 7, {"status": "completed"})
assert not ok and stale == before_stale and state == before_stale
ok, state = apply_write(state, 8, {"status": "completed"})
assert ok and state["version"] == 9 and state["status"] == "completed"
print("PASS: L13.10 reference answer rejects stale writes without mutating current state")
