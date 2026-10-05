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

assert application_decision(proposals[0]) == "answer_without_tool"
assert application_decision(proposals[1]) == "execute_read"
assert application_decision(proposals[2]) == "request_approval"
