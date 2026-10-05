#!/usr/bin/env python3
"""Learner exercise for L11.07: rank tools without selecting forbidden capability."""

TOOLS = {
    "get_order": {"provides": {"order_status", "region", "item_type"}, "side_effect": False, "permitted": True},
    "get_refund_policy": {"provides": {"refund_policy"}, "side_effect": False, "permitted": True},
    "refund_order": {"provides": {"refund_result"}, "side_effect": True, "permitted": False},
}
NEEDED = {"region", "item_type"}


def score(spec):
    # TODO 1: make a forbidden tool impossible to win.
    # TODO 2: reward useful fields.
    # TODO 3: apply a small cost to side-effecting tools.
    raise NotImplementedError("TODO: implement tool scoring")


ranked = sorted(TOOLS.items(), key=lambda item: score(item[1]), reverse=True)
assert ranked[0][0] == "get_order"
assert score(TOOLS["refund_order"]) < 0
print("PASS: learner selector prefers useful permitted capability")
