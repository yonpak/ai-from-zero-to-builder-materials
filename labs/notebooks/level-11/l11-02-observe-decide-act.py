#!/usr/bin/env python3

TOOL_RESULTS = {
    "get_order": {"status": "delivered", "damaged": True},
    "check_refund_policy": {"policy": "approval_required"},
}

state = {
    "goal": "resolve order 4172",
    "order_status": "unknown",
    "damaged": None,
    "step": 0,
}

action = "get_order"
cycles = 0

while True:
    observation = TOOL_RESULTS[action]

    if action == "get_order":
        state["order_status"] = observation["status"]
        state["damaged"] = observation["damaged"]
        decision = (
            "check_refund_policy"
            if observation["status"] == "delivered"
            else "report_shipping"
        )
    elif action == "check_refund_policy":
        state["policy"] = observation["policy"]
        decision = (
            "request_approval"
            if observation["policy"] == "approval_required"
            else "finish"
        )
    else:
        raise RuntimeError(f"unexpected action: {action}")

    cycles += 1
    state["step"] = cycles
    print(
        f"cycle {cycles}: {action} -> {decision}",
        {"observation": observation, "state": dict(state)},
    )

    if decision in {"report_shipping", "request_approval", "finish"}:
        print(f"stopped at: {decision} after {cycles} cycle(s)")
        break

    action = decision
