#!/usr/bin/env python3
"""L13.6 local Lab: trust checks run in order, starting with who we are talking to."""
policy = {
    "endpoints": {"https://mcp.example.internal"},
    "roles": {"reader": {"get_order"}},
    "max_scopes": {"reader": {"orders.read"}},
    "allowed_fields": {"order_id"},
}
request = {
    "endpoint": "https://mcp.example.internal",
    "role": "reader",
    "capability": "get_order",
    "scopes": {"orders.read"},
    "fields": {"order_id": "4172"},
}
checks = [
    ("endpoint approved", request["endpoint"] in policy["endpoints"]),
    ("capability allowed for role", request["capability"] in policy["roles"][request["role"]]),
    ("scopes within role maximum", request["scopes"] <= policy["max_scopes"][request["role"]]),
    ("only needed data fields sent", set(request["fields"]) <= policy["allowed_fields"]),
]
for name, ok in checks:
    print(f"{'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print("trusted: False (stopped at first failed check)")
        raise SystemExit(1)
print("trusted: True")
print("PASS: endpoint, capability, scope, and data minimization are checked")
