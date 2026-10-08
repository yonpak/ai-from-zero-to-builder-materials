#!/usr/bin/env python3
parent_tools={"read_logs","search_docs","refund_order"}
# The parent grants this subgoal only the read tools it needs.
delegated_scope={"read_logs","search_docs"}
delegation={
 "subgoal":"find first failing request",
 "allowed_tools":["read_logs","search_docs"],
 "step_budget":4,
 "expected_fields":["request_id","timestamp","evidence"],
}
outside_scope=sorted(set(delegation["allowed_tools"])-delegated_scope)
budget_ok=1<=delegation["step_budget"]<=4
evidence_ok="evidence" in delegation["expected_fields"]
valid=not outside_scope and budget_ok and evidence_ok
print("requested tools:",delegation["allowed_tools"])
print("outside delegated scope:",outside_scope)
print("delegation_valid:",valid)
# Invariant: a delegation that asks for a tool outside its scope is never accepted.
assert not (valid and outside_scope)
assert delegated_scope<=parent_tools
print("PASS: delegation is accepted only inside its tool scope, budget, and evidence contract")
