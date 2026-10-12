#!/usr/bin/env python3
"""Reference answer for L15.07."""


def authorize(principal, proposal, policy):
    role = principal.get("role")
    action = proposal.get("action")
    return action in set(policy.get(role, []))


policy = {"support": ["read_order"], "admin": ["read_order", "refund_order"]}
support = {"user_id": "u-17", "role": "support"}
admin = {"user_id": "u-99", "role": "admin"}

assert authorize(support, {"action": "read_order", "role": "admin"}, policy)
assert not authorize(support, {"action": "refund_order", "role": "admin"}, policy)
assert authorize(admin, {"action": "refund_order", "role": "support"}, policy)
assert not authorize({"user_id": "u-x"}, {"action": "read_order"}, policy)
print("PASS: L15.07 reference answer authorizes from trusted principal role, not generated role text")
