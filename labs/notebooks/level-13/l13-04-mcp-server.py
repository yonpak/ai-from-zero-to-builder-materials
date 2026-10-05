#!/usr/bin/env python3
"""L13.4 preflight: a server boundary validates each call before any business code runs.

This is a deterministic preflight, not a wire-level MCP server.
"""
PINNED = "2026-07-28"
TOOLS = {"get_order_status": {"required": {"order_id": str}, "side_effect": False}}
business_calls = []


def get_order_status(order_id):  # the mock business function
    business_calls.append(order_id)
    return {"order_id": order_id, "status": "delivered"}


def validate(req):
    if req.get("protocol_version") != PINNED:
        return "unsupported_version"
    name = req.get("name")
    if name not in TOOLS:
        return "unknown_tool"
    args = req.get("arguments", {})
    for field, typ in TOOLS[name]["required"].items():
        if not isinstance(args.get(field), typ):
            return "invalid_arguments"
    return "ok"


def handle(req):
    verdict = validate(req)
    if verdict != "ok":
        return {"error": verdict}
    return {"result": get_order_status(**req["arguments"])}


request = {"protocol_version": PINNED, "name": "get_order_status", "arguments": {"order_id": "4172"}}
print("request:", request)
print("response:", handle(request))
print("business function calls:", len(business_calls))

good = {"protocol_version": PINNED, "name": "get_order_status", "arguments": {"order_id": "4172"}}

# A valid request must pass validation and reach business code exactly once.
assert validate(good) == "ok"
before_good = len(business_calls)
assert handle(good) == {"result": {"order_id": "4172", "status": "delivered"}}
assert len(business_calls) == before_good + 1

# Invalid requests must be rejected before business code runs.
before_rejected = len(business_calls)
assert handle({**good, "name": "admin_anything"}) == {"error": "unknown_tool"}
assert handle({**good, "arguments": {"order_id": 4172}}) == {"error": "invalid_arguments"}
assert len(business_calls) == before_rejected
print("PASS: server boundary admits valid calls and rejects malformed calls before business code")
