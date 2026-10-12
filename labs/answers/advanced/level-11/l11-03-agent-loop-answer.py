#!/usr/bin/env python3
"""Reference answer for L11.03."""


def run(actions, max_steps=4, repeat_limit=3):
    seen = {}
    for action in actions[:max_steps]:
        seen[action] = seen.get(action, 0) + 1
        if action == "finish":
            return "success"
        if seen[action] >= repeat_limit:
            return "repeated_action"
    return "max_steps"


assert run(["get_order", "check_policy", "finish"]) == "success"
assert run(["search_order", "search_order", "search_order", "search_order"]) == "repeated_action"
assert run(["a", "b", "finish"], max_steps=2) == "max_steps"
assert run(["finish"], max_steps=0) == "max_steps"
assert run(["x", "x"], repeat_limit=2) == "repeated_action"
print("PASS: L11.03 reference answer enforces success, repetition, and step budget")
