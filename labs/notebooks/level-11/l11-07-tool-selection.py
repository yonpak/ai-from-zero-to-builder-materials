#!/usr/bin/env python3

tools = {
    "get_order": {
        "provides": {"order_status", "region", "item_type"},
        "side_effect": False,
        "permitted": True,
    },
    "get_refund_policy": {
        "provides": {"refund_policy"},
        "side_effect": False,
        "permitted": True,
    },
    "refund_order": {
        "provides": {"refund_result"},
        "side_effect": True,
        "permitted": False,
    },
}

known_fields = {"order_id"}
needed_fields = {"region", "item_type", "refund_policy"}
still_missing = needed_fields - known_fields


def score(spec):
    if not spec["permitted"]:
        return -100
    gain = len(spec["provides"] & still_missing)
    return gain * 10 - (5 if spec["side_effect"] else 0)


ranked = sorted(
    tools.items(),
    key=lambda item: (-score(item[1]), item[0]),
)
print("known_fields:", sorted(known_fields))
print("still missing:", sorted(still_missing))
print("ranking:", [(name, score(spec)) for name, spec in ranked])
print("selected:", ranked[0][0])
