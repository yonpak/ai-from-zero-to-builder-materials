#!/usr/bin/env python3
principal_customer_id = "c-1"
state = "ORDER_LOADED"

requests = [
    {"order_id": "4172", "customer_id": "c-1", "quantity": 2},
    {"order_id": "4172", "customer_id": "c-2", "quantity": 2},
    {"order_id": "4172", "customer_id": "c-1", "quantity": 9},
]

def validate_request(request, stock=5):
    if set(request) != {"order_id", "customer_id", "quantity"}:
        return "schema"
    if not isinstance(request["quantity"], int):
        return "schema"
    if not 1 <= request["quantity"] <= stock:
        return "domain"
    if request["customer_id"] != principal_customer_id:
        return "permission"
    if state != "ORDER_LOADED":
        return "state"
    return "ok"

for request in requests:
    print(request, "->", validate_request(request))

# Invariant for any logged-in user: "ok" only for that user's own, in-stock request.
for request in requests:
    if validate_request(request) == "ok":
        assert request["customer_id"] == principal_customer_id
        assert 1 <= request["quantity"] <= 5
print("PASS: only the session's own, in-stock requests are accepted")
