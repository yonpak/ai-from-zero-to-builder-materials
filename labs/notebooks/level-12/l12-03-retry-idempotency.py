#!/usr/bin/env python3
ledger={}
reuse_operation_id=True

def refund(operation_id, amount):
    if operation_id in ledger:
        return ledger[operation_id]
    ledger[operation_id]={"receipt":f"r-{len(ledger)+1}","amount":amount}
    return ledger[operation_id]

first_id="refund:4172:20"
second_id=first_id if reuse_operation_id else "refund:4172:20:retry"
first=refund(first_id,20)
second=refund(second_id,20)
print("first:",first)
print("second:",second)
print("effect_count:",len(ledger))
assert len(ledger)==1
print("PASS: stable operation identity prevents duplicate effect")
