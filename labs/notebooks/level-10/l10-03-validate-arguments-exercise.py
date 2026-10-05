#!/usr/bin/env python3
"""Learner exercise for L10.03: validate structured tool arguments."""

PRINCIPAL_CUSTOMER_ID = "c-1"
STATE = "ORDER_LOADED"


def validate_request(request, stock=5):
    # TODO 1: require exactly order_id, customer_id, and quantity.
    # TODO 2: enforce quantity type and stock/domain bounds.
    # TODO 3: enforce principal ownership and the required workflow state.
    raise NotImplementedError("TODO: implement request validation")


requests = [
    {"order_id": "4172", "customer_id": "c-1", "quantity": 2},
    {"order_id": "4172", "customer_id": "c-2", "quantity": 2},
    {"order_id": "4172", "customer_id": "c-1", "quantity": 9},
]
assert [validate_request(r) for r in requests] == ["ok", "permission", "domain"]
print("PASS: learner validator separates schema, domain, permission, and state checks")
