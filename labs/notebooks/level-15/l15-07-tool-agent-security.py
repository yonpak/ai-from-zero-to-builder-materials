#!/usr/bin/env python3
from __future__ import annotations
import json

def authorize(principal: dict, proposal: dict, policy: dict) -> bool:
    role = principal.get("role")
    action = proposal.get("action")
    return action in set(policy.get(role, []))

if __name__ == "__main__":
    principal = {"user_id":"u-17","role":"support"}
    proposal = {"action":"read_order","order_id":"4172","role":"admin"}
    policy = {"support":["read_order"],"admin":["read_order","refund_order"]}
    print(json.dumps({
        "authorized": authorize(principal, proposal, policy),
        "trusted_role": principal["role"],
        "generated_role_ignored": proposal["role"],
    }, sort_keys=True))
