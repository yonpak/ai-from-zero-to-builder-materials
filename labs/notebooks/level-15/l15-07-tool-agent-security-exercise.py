#!/usr/bin/env python3
"""Learner exercise for L15.07: authorize a tool action from trusted principal identity."""


def authorize(principal, proposal, policy):
    # TODO 1: read the role from the trusted principal, not generated proposal text.
    # TODO 2: read the proposed action.
    # TODO 3: allow only actions listed for that trusted role.
    raise NotImplementedError("TODO: implement trusted-principal authorization")


policy = {"support": ["read_order"], "admin": ["read_order", "refund_order"]}
principal = {"user_id": "u-17", "role": "support"}
spoofed = {"action": "refund_order", "order_id": "4172", "role": "admin"}
safe = {"action": "read_order", "order_id": "4172", "role": "admin"}
assert not authorize(principal, spoofed, policy)
assert authorize(principal, safe, policy)
print("PASS: learner authorization ignores generated role escalation")
