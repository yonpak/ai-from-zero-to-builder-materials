#!/usr/bin/env python3
"""Reference answer for L10.06."""

TRANSITIONS = {
    ("START", "order_loaded"): "ORDER_LOADED",
    ("ORDER_LOADED", "approval_required"): "AWAITING_APPROVAL",
    ("AWAITING_APPROVAL", "approved"): "APPROVED",
    ("APPROVED", "refund_requested"): "REFUND_REQUESTED",
    ("REFUND_REQUESTED", "refund_succeeded"): "DONE",
}


def run_trace(events):
    state = "START"
    for event in events:
        key = (state, event)
        if key not in TRANSITIONS:
            raise ValueError(f"illegal transition: {state} + {event}")
        state = TRANSITIONS[key]
    return state


valid = ["order_loaded", "approval_required", "approved", "refund_requested", "refund_succeeded"]
assert run_trace(valid) == "DONE"
assert run_trace([]) == "START"
for invalid in [
    ["approval_required"],
    ["order_loaded", "approved"],
    ["order_loaded", "approval_required", "refund_requested"],
]:
    try:
        run_trace(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"illegal trace accepted: {invalid}")
print("PASS: L10.06 reference answer enforces explicit workflow transitions")
