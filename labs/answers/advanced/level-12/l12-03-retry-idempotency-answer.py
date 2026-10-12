#!/usr/bin/env python3
"""Reference answer for L12.03."""

ledger = {}


def refund(operation_id, amount):
    if operation_id in ledger:
        return ledger[operation_id]
    result = {"receipt": f"r-{len(ledger)+1}", "amount": amount}
    ledger[operation_id] = result
    return result


first = refund("refund:4172:20", 20)
second = refund("refund:4172:20", 20)
assert first == second
assert len(ledger) == 1
assert refund("refund:4172:20", 999)["amount"] == 20
third = refund("refund:4172:30", 30)
assert third != first
assert len(ledger) == 2
print("PASS: L12.03 reference answer reuses completed operations and separates new identities")
