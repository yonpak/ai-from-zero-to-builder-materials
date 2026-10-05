#!/usr/bin/env python3
policy={"reader":{"get_order"},"operator":{"get_order","refund_order"}}
fixtures=[
 {"id":"ok","role":"reader","action":"get_order","executed":True,"expected_valid":True},
 {"id":"unauthorized","role":"reader","action":"refund_order","executed":True,"expected_valid":False},
]
for f in fixtures:
    authorized=f["action"] in policy[f["role"]]
    valid=not f["executed"] or authorized
    print(f["id"],valid)
    assert valid is f["expected_valid"]
print("PASS: fixtures recompute policy from raw role and action")
