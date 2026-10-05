#!/usr/bin/env python3
"""L13.2 local Lab: tools and resources get different controls."""
entries = [
    {"kind": "tool", "name": "get_ticket", "side_effect": False},
    {"kind": "tool", "name": "create_ticket", "side_effect": True},
    {"kind": "resource", "name": "incident_handbook", "freshness_seconds": 300},
]


def controls_for(entry):
    if entry["kind"] == "tool":
        return {
            "schema": True,
            "authorization": True,
            "needs_approval": entry["side_effect"],
            "needs_idempotency_key": entry["side_effect"],
        }
    if entry["kind"] == "resource":
        return {
            "scope": True,
            "provenance": True,
            "freshness_limit_s": entry["freshness_seconds"],
        }
    raise ValueError(f"unknown entry kind: {entry['kind']!r}")


for e in entries:
    print(f"{e['kind']:8s} {e['name']:17s}", controls_for(e))

safe_tool = controls_for({"kind": "tool", "name": "read", "side_effect": False})
effect_tool = controls_for({"kind": "tool", "name": "write", "side_effect": True})
resource = controls_for({"kind": "resource", "name": "guide", "freshness_seconds": 60})
assert safe_tool["authorization"] is True and safe_tool["needs_approval"] is False
assert effect_tool["needs_approval"] is True and effect_tool["needs_idempotency_key"] is True
assert resource == {"scope": True, "provenance": True, "freshness_limit_s": 60}
print("PASS: tool and resource controls remain distinct")
