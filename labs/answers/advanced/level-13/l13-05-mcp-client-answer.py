#!/usr/bin/env python3
"""Reference answer for L13.05."""

CATALOG = [
    {"name": "get_order", "version": "2026-07-28", "roles": {"reader", "operator"}},
    {"name": "refund_order", "version": "2026-07-28", "roles": {"operator"}},
    {"name": "old_tool", "version": "2025-11-25", "roles": {"reader"}},
]


def exposed_tools(catalog, role, protocol_version):
    return [
        item["name"]
        for item in catalog
        if item["version"] == protocol_version and role in item["roles"]
    ]


assert exposed_tools(CATALOG, "reader", "2026-07-28") == ["get_order"]
assert exposed_tools(CATALOG, "operator", "2026-07-28") == ["get_order", "refund_order"]
assert exposed_tools(CATALOG, "reader", "2025-11-25") == ["old_tool"]
assert exposed_tools(CATALOG, "guest", "2026-07-28") == []
print("PASS: L13.05 reference answer filters discovery by protocol version and local role")
