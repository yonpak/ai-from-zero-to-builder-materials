#!/usr/bin/env python3
"""Reference answer for L10.02. Kept outside the learner Lab path."""

schema = {
    "required": {"customer_id"},
    "properties": {
        "customer_id": str,
        "status": {"open", "shipped", "closed"},
        "limit": range(1, 21),
    },
    "additional_properties_allowed": False,
}


def validate(args, spec):
    missing = spec["required"] - args.keys()
    if missing:
        return False, f"missing={sorted(missing)}"

    if not spec["additional_properties_allowed"]:
        extra = set(args) - spec["properties"].keys()
        if extra:
            return False, f"extra={sorted(extra)}"

    for key, value in args.items():
        rule = spec["properties"].get(key)
        if rule is None:
            continue
        if isinstance(rule, type) and not isinstance(value, rule):
            return False, f"{key}: wrong type"
        if isinstance(rule, set) and value not in rule:
            return False, f"{key}: not allowed"
        if isinstance(rule, range) and value not in rule:
            return False, f"{key}: outside range"
    return True, "ok"


assert validate({"customer_id": "c-1"}, schema) == (True, "ok")
assert validate({"status": "open"}, schema)[1].startswith("missing=")
assert validate({"customer_id": "c-1", "debug": True}, schema)[1].startswith("extra=")
assert validate({"customer_id": 7}, schema) == (False, "customer_id: wrong type")
assert validate({"customer_id": "c-1", "status": "pending"}, schema) == (False, "status: not allowed")
assert validate({"customer_id": "c-1", "limit": 50}, schema) == (False, "limit: outside range")
print("PASS: L10.02 reference answer covers required, extra, type, enum, and range validation")
