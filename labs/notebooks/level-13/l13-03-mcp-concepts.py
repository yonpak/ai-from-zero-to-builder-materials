#!/usr/bin/env python3
"""L13.3 local Lab: check a pinned MCP request fixture before sending it."""
PINNED = "2026-07-28"  # the protocol version this course pins; see the Lesson's version note
request = {
    "protocol_version": PINNED,
    "client_info": {"name": "course-client", "version": "1.0"},
    "method": "tools/call",
    "name": "search",
}
discovered = {"tools": ["search", "get_order"]}

problems = []
if request["protocol_version"] != PINNED:
    problems.append(f"protocol version {request['protocol_version']} does not match pinned {PINNED}")
if request["name"] not in discovered["tools"]:
    problems.append(f"tool '{request['name']}' was not discovered")
print({"protocol_version": request["protocol_version"], "method": request["method"],
       "name": request["name"], "discovered_tools": discovered["tools"]})
if problems:
    for p in problems:
        print("INCOMPATIBLE:", p)
    raise SystemExit(1)
print("PASS: pinned MCP request and discovery fixture are compatible")
