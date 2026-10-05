#!/usr/bin/env python3
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
print("valid final state:", run_trace(valid))

try:
    run_trace(["order_loaded", "approval_required", "refund_requested"])
except ValueError as error:
    print("blocked:", error)
else:
    raise AssertionError("approval skip should be blocked")
