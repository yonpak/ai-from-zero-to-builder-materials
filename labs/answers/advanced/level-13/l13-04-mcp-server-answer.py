#!/usr/bin/env python3
"""Reference answer for the deterministic L13.04 MCP boundary preflight."""

PINNED = "2026-07-28"
TOOLS = {"get_order_status": {"required": {"order_id": str}, "side_effect": False}}


def validate(request):
    if request.get("protocol_version") != PINNED:
        return "unsupported_version"
    name = request.get("name")
    if name not in TOOLS:
        return "unknown_tool"
    arguments = request.get("arguments", {})
    if not isinstance(arguments, dict):
        return "invalid_arguments"
    for field, expected_type in TOOLS[name]["required"].items():
        if not isinstance(arguments.get(field), expected_type):
            return "invalid_arguments"
    return "ok"


good = {"protocol_version": PINNED, "name": "get_order_status", "arguments": {"order_id": "4172"}}
assert validate(good) == "ok"
assert validate({**good, "protocol_version": "2025-11-25"}) == "unsupported_version"
assert validate({**good, "name": "admin_anything"}) == "unknown_tool"
assert validate({**good, "arguments": {}}) == "invalid_arguments"
assert validate({**good, "arguments": {"order_id": 4172}}) == "invalid_arguments"
assert validate({**good, "arguments": "order_id=4172"}) == "invalid_arguments"
print("PASS: L13.04 reference answer validates version, tool declaration, and required argument types")
