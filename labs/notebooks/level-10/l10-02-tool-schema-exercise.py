#!/usr/bin/env python3
"""Learner exercise for L10.02: validate a narrow tool schema."""

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
    # TODO 1: reject missing required fields.
    # TODO 2: reject unexpected fields when additional properties are disabled.
    # TODO 3: enforce type, enum, and range rules for declared fields.
    raise NotImplementedError("TODO: implement schema validation")


cases = [
    ({"customer_id": "c-1", "status": "open", "limit": 5}, (True, "ok")),
    ({"status": "open"}, (False, "missing")),
    ({"customer_id": "c-1", "limit": 50}, (False, "limit")),
    ({"customer_id": "c-1", "debug": True}, (False, "extra")),
]

for candidate, expected in cases:
    actual = validate(candidate, schema)
    assert actual[0] is expected[0]
    assert expected[1] in actual[1]
print("PASS: learner schema validator handles required, extra, enum/type, and range boundaries")
