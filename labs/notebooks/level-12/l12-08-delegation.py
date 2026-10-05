#!/usr/bin/env python3
parent_tools={"read_logs","search_docs","refund_order"}
delegation={
 "subgoal":"find first failing request",
 "allowed_tools":["read_logs","search_docs"],
 "step_budget":4,
 "expected_fields":["request_id","timestamp","evidence"],
}
forbidden=set(delegation["allowed_tools"])-{"read_logs","search_docs"}
valid=not forbidden and 1<=delegation["step_budget"]<=4 and "evidence" in delegation["expected_fields"]
print("delegation_valid:",valid)
assert valid
assert "refund_order" not in delegation["allowed_tools"]
print("PASS: delegation narrows tools, budget, and return evidence")
