#!/usr/bin/env python3
catalog=[
 {"name":"get_order","version":"2026-07-28","roles":{"reader","operator"}},
 {"name":"refund_order","version":"2026-07-28","roles":{"operator"}},
 {"name":"old_tool","version":"2025-11-25","roles":{"reader"}},
]
role="reader"
exposed=[x["name"] for x in catalog if x["version"]=="2026-07-28" and role in x["roles"]]
print("exposed:",exposed)
print("remote catalog size:",len(catalog))
assert "old_tool" not in exposed
assert all(role in x["roles"] for x in catalog if x["name"] in exposed)
print("PASS: client filters discovery through version and local role policy")
