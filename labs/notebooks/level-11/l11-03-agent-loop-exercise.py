#!/usr/bin/env python3
"""Learner exercise for L11.03: implement a bounded agent loop."""


def run(actions, max_steps=4, repeat_limit=3):
    # TODO 1: count every attempted action up to max_steps.
    # TODO 2: return success when action == "finish".
    # TODO 3: stop when one normalized action reaches repeat_limit.
    raise NotImplementedError("TODO: implement bounded loop control")


assert run(["get_order", "check_policy", "finish"]) == "success"
assert run(["search_order", "search_order", "search_order", "search_order"]) == "repeated_action"
assert run(["a", "b", "c"], max_steps=2) == "max_steps"
print("PASS: learner loop enforces success, repetition, and step-budget terminals")
