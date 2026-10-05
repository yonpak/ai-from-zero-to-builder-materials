#!/usr/bin/env python3
"""Learner exercise for L13.04: implement the deterministic MCP server preflight boundary."""

PINNED = "2026-07-28"
TOOLS = {"get_order_status": {"required": {"order_id": str}, "side_effect": False}}


def validate(request):
    # TODO 1: reject unsupported protocol versions.
    # TODO 2: reject undeclared tools.
    # TODO 3: validate each required argument type.
    raise NotImplementedError("TODO: implement MCP server-boundary validation")


good = {"protocol_version": PINNED, "name": "get_order_status", "arguments": {"order_id": "4172"}}
assert validate(good) == "ok"
assert validate({**good, "protocol_version": "2025-11-25"}) == "unsupported_version"
assert validate({**good, "name": "admin_anything"}) == "unknown_tool"
assert validate({**good, "arguments": {"order_id": 4172}}) == "invalid_arguments"
print("PASS: learner MCP preflight rejects incompatible, undeclared, and malformed calls")
