#!/usr/bin/env python3
proposals = [
    {"id": "answer_from_context", "tool": None, "approved": False},
    {"id": "read_order", "tool": "get_order", "approved": False},
    {"id": "refund_order", "tool": "refund_order", "approved": False},
]

READ_ONLY = {"get_order"}

def application_decision(proposal):
    if proposal["tool"] is None:
        return "answer_without_tool"
    if proposal["tool"] in READ_ONLY:
        return "execute_read"
    if proposal["tool"] == "refund_order":
        return "execute_action" if proposal["approved"] else "request_approval"
    return "reject_unknown_tool"

for proposal in proposals:
    print(proposal["id"], "->", application_decision(proposal))

# Invariants that hold for any approval state the application records:
for proposal in proposals:
    decision = application_decision(proposal)
    if proposal["tool"] in READ_ONLY:
        assert decision == "execute_read"
    if proposal["tool"] == "refund_order" and not proposal["approved"]:
        assert decision == "request_approval"
print("PASS: a refund runs only after application-owned approval")
