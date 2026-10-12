#!/usr/bin/env python3
"""Reference answer for L11.07."""

TOOLS = {
    "get_order": {"provides": {"order_status", "region", "item_type"}, "side_effect": False, "permitted": True},
    "get_refund_policy": {"provides": {"refund_policy"}, "side_effect": False, "permitted": True},
    "refund_order": {"provides": {"refund_result"}, "side_effect": True, "permitted": False},
}
NEEDED = {"region", "item_type"}


def score(spec, needed=NEEDED):
    if not spec["permitted"]:
        return -100
    gain = len(spec["provides"] & needed)
    return gain * 10 - (5 if spec["side_effect"] else 0)


ranked = sorted(TOOLS.items(), key=lambda item: score(item[1]), reverse=True)
assert ranked[0][0] == "get_order"
assert score(TOOLS["refund_order"]) == -100
assert score({"provides": {"region"}, "side_effect": False, "permitted": True}) > score(
    {"provides": set(), "side_effect": False, "permitted": True}
)
assert score({"provides": {"region"}, "side_effect": True, "permitted": True}) < score(
    {"provides": {"region"}, "side_effect": False, "permitted": True}
)
print("PASS: L11.07 reference answer ranks useful permitted tools and penalizes side effects")
