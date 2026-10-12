#!/usr/bin/env python3
"""Reference answer for L10.03 with boundary tests for every exercise requirement."""

PRINCIPAL_CUSTOMER_ID = "c-1"
STATE = "ORDER_LOADED"


def validate_request(request, stock=5):
    if set(request) != {"order_id", "customer_id", "quantity"}:
        return "schema"
    if not isinstance(request["order_id"], str) or not isinstance(request["customer_id"], str):
        return "schema"
    if not isinstance(request["quantity"], int) or isinstance(request["quantity"], bool):
        return "schema"
    if not 1 <= request["quantity"] <= stock:
        return "domain"
    if request["customer_id"] != PRINCIPAL_CUSTOMER_ID:
        return "permission"
    if STATE != "ORDER_LOADED":
        return "state"
    return "ok"


valid = {"order_id": "4172", "customer_id": "c-1", "quantity": 2}
assert validate_request(valid) == "ok"
assert validate_request({"order_id": "4172", "customer_id": "c-1"}) == "schema"
assert validate_request({**valid, "debug": True}) == "schema"
assert validate_request({**valid, "quantity": "2"}) == "schema"
assert validate_request({**valid, "quantity": 0}) == "domain"
assert validate_request({**valid, "quantity": 9}) == "domain"
assert validate_request({**valid, "customer_id": "c-2"}) == "permission"

STATE = "AWAITING_APPROVAL"
assert validate_request(valid) == "state"
STATE = "ORDER_LOADED"
assert validate_request(valid) == "ok"

print("PASS: L10.03 reference answer covers schema, domain, permission, and workflow state")
