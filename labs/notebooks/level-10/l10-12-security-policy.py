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
# Invariant for any approval: "allow" needs both the role permission and an exact approval match.
for role in policy:
    if decision(role, proposal) == "allow":
        assert proposal["tool"] in policy[role]
        assert proposal["approved_amount"] == proposal["amount"]
print("PASS: role permission and approval binding are both required")
