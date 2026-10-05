#!/usr/bin/env python3
cases=[
 {"name":"ok","expected":"2026-07-28","observed":"2026-07-28","capability":"read_order","allowed":{"read_order"}},
 {"name":"version-mismatch","expected":"2026-07-28","observed":"2025-11-25","capability":"read_order","allowed":{"read_order"}},
 {"name":"policy-denied","expected":"2026-07-28","observed":"2026-07-28","capability":"delete_order","allowed":{"read_order"}},
]


def decide(case):
    compatible=case["expected"]==case["observed"]
    authorized=case["capability"] in case["allowed"]
    if not compatible:
        decision="reject: protocol version mismatch"
    elif not authorized:
        decision="reject: capability not allowed by policy"
    else:
        decision="call"
    return compatible, authorized, decision


for case in cases:
    compatible, authorized, decision=decide(case)
    print(f'{case["name"]:17s}',{"compatible":compatible,"authorized":authorized},"=>",decision)

assert decide({"expected":"v1","observed":"v1","capability":"read","allowed":{"read"}})[2]=="call"
assert decide({"expected":"v1","observed":"v0","capability":"read","allowed":{"read"}})[2]=="reject: protocol version mismatch"
assert decide({"expected":"v1","observed":"v1","capability":"delete","allowed":{"read"}})[2]=="reject: capability not allowed by policy"
print("PASS: compatibility and authorization are separate")
