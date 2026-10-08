#!/usr/bin/env python3
policy={"reader":{"get_order"},"operator":{"get_order","refund_order"}}
# "authorized" is a stored, derived claim. The validator ignores it and recomputes policy.
fixtures=[
 {"id":"ok","role":"reader","action":"get_order","executed":True,"authorized":True,"expected_valid":True},
 {"id":"unauthorized","role":"reader","action":"refund_order","executed":True,"authorized":False,"expected_valid":False},
]
for f in fixtures:
    authorized=f["action"] in policy[f["role"]]
    valid=not f["executed"] or authorized
    reason="ok" if valid else f"rule: {f['role']} may not execute {f['action']}"
    print(f"{f['id']}: stored authorized={f['authorized']} recomputed authorized={authorized} valid={valid} ({reason})")
    assert valid is f["expected_valid"]
print("PASS: fixtures recompute policy from raw role and action")
