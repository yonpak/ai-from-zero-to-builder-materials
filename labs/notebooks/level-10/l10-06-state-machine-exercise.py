#!/usr/bin/env python3
"""Learner exercise for L10.06: implement explicit workflow transitions."""

TRANSITIONS = {
    ("START", "order_loaded"): "ORDER_LOADED",
    ("ORDER_LOADED", "approval_required"): "AWAITING_APPROVAL",
    ("AWAITING_APPROVAL", "approved"): "APPROVED",
    ("APPROVED", "refund_requested"): "REFUND_REQUESTED",
    ("REFUND_REQUESTED", "refund_succeeded"): "DONE",
}


def run_trace(events):
    # TODO 1: start from START.
    # TODO 2: apply only transitions present in TRANSITIONS.
    # TODO 3: raise ValueError on an illegal transition.
    raise NotImplementedError("TODO: implement the state machine")


valid = ["order_loaded", "approval_required", "approved", "refund_requested", "refund_succeeded"]
assert run_trace(valid) == "DONE"
try:
    run_trace(["order_loaded", "approval_required", "refund_requested"])
except ValueError:
    pass
else:
    raise AssertionError("approval skip must be blocked")
print("PASS: learner state machine accepts the valid trace and blocks an approval skip")
