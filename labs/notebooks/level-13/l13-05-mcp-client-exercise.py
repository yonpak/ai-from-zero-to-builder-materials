#!/usr/bin/env python3
"""Learner exercise for L13.05: filter discovered capabilities with local policy."""

CATALOG = [
    {"name": "get_order", "version": "2026-07-28", "roles": {"reader", "operator"}},
    {"name": "refund_order", "version": "2026-07-28", "roles": {"operator"}},
    {"name": "old_tool", "version": "2025-11-25", "roles": {"reader"}},
]


def exposed_tools(catalog, role, protocol_version):
    # TODO 1: keep only capabilities matching the negotiated protocol version.
    # TODO 2: keep only capabilities allowed for the local role.
    raise NotImplementedError("TODO: implement local discovery filtering")


assert exposed_tools(CATALOG, "reader", "2026-07-28") == ["get_order"]
assert exposed_tools(CATALOG, "operator", "2026-07-28") == ["get_order", "refund_order"]
print("PASS: learner MCP client filters discovery through compatibility and local authority")
