#!/usr/bin/env python3
"""Learner exercise for L12.03: make a retry-safe side effect."""

ledger = {}


def refund(operation_id, amount):
    # TODO 1: return the recorded result when operation_id already exists.
    # TODO 2: create exactly one new receipt for a new operation_id.
    raise NotImplementedError("TODO: implement idempotent effect handling")


first = refund("refund:4172:20", 20)
second = refund("refund:4172:20", 20)
assert first == second
assert len(ledger) == 1
print("PASS: learner retry path reuses the original side effect")
