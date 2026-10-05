#!/usr/bin/env python3
RETRYABLE = {"timeout", "rate_limit", "server"}

def next_action(category, attempt, max_attempts=2, side_effect=False, idempotent=False):
    if category in {"validation", "permission", "not_found"}:
        return "stop_or_repair"
    if category not in RETRYABLE:
        return "stop"
    if attempt >= max_attempts:
        return "stop_budget"
    if side_effect and not idempotent:
        return "check_completion_before_retry"
    return "retry"

cases = [
    ("validation", 0, False, False),
    ("timeout", 0, False, False),
    ("timeout", 0, True, False),
    ("rate_limit", 2, False, False),
]
for category, attempt, side_effect, idempotent in cases:
    print(category, "->", next_action(category, attempt, 2, side_effect, idempotent))

assert next_action("timeout", 0) == "retry"
assert next_action("timeout", 0, side_effect=True) == "check_completion_before_retry"
