MAX_RECENT = 3
events = [
    {"source": "order_tool", "order_status": "shipping"},
    {"source": "order_tool", "order_status": "delivered"},
    {"source": "policy_tool", "refund_eligible": True},
    {"source": "approval_service", "approval_status": "pending"},
]

state = {"step_count": 0, "recent": []}
for event in events:
    state["step_count"] += 1
    if "order_status" in event:
        state["order_status"] = event["order_status"]
        state["order_status_source"] = event["source"]
    if "refund_eligible" in event:
        state["refund_eligible"] = event["refund_eligible"]
    if "approval_status" in event:
        state["approval_status"] = event["approval_status"]
    state["recent"] = (state["recent"] + [event])[-MAX_RECENT:]

print("working state:", state)
print("audit event count:", len(events))
