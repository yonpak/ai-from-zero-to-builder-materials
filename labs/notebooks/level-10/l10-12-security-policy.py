#!/usr/bin/env python3
policy = {
    "reader": {"get_order"},
    "operator": {"get_order", "refund_order"},
}
proposal = {"tool": "refund_order", "amount": 120, "approved_amount": 100}

def decision(role, item):
    if item["tool"] not in policy.get(role, set()):
        return "deny_tool"
    if item["tool"] == "refund_order" and item["approved_amount"] != item["amount"]:
        return "deny_approval_mismatch"
    return "allow"

print("reader:", decision("reader", proposal))
print("operator:", decision("operator", proposal))
assert decision("reader", proposal) == "deny_tool"
assert decision("operator", proposal) == "deny_approval_mismatch"
