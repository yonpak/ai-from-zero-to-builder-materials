plan = [
    {"name": "get order status", "status": "pending"},
    {"name": "check refund eligibility", "status": "pending"},
    {"name": "request approval if needed", "status": "pending"},
]

observations = [
    {"order_status": "delivered"},
    {"eligible": False},
]

for obs in observations:
    if obs.get("order_status"):
        plan[0]["status"] = "completed"
        plan[1]["status"] = "active"
    if "eligible" in obs:
        plan[1]["status"] = "completed"
        plan[2]["status"] = "pending" if obs["eligible"] else "skipped"
    print("observation:", obs)
    print("plan:", plan)
