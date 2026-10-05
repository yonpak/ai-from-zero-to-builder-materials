#!/usr/bin/env python3
schema = {
    "required": {"customer_id"},
    "properties": {
        "customer_id": str,
        "status": {"open", "shipped", "closed"},
        "limit": range(1, 21),
    },
    "additional_properties_allowed": False,
}

candidates = [
    {"customer_id": "c-1", "status": "open", "limit": 5},
    {"status": "open"},
    {"customer_id": "c-1", "limit": 50},
    {"customer_id": "c-1", "debug": True},
]

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

for item in candidates:
    print(item, "->", validate(item, schema))
