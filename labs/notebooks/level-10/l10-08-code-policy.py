#!/usr/bin/env python3
policy = {
    "network": False,
    "max_seconds": 3,
    "max_output_bytes": 2000,
    "writable_roots": {"/workspace"},
}

requests = [
    {"id": "calc", "network": False, "seconds": 1, "output_bytes": 100, "write_path": None},
    {"id": "web", "network": True, "seconds": 1, "output_bytes": 100, "write_path": None},
    {"id": "large-output", "network": False, "seconds": 1, "output_bytes": 5000, "write_path": None},
]

def check(job):
    if job["network"] and not policy["network"]:
        return "policy_blocked_network"
    if job["seconds"] > policy["max_seconds"]:
        return "resource_limit_time"
    if job["output_bytes"] > policy["max_output_bytes"]:
        return "resource_limit_output"
    if job["write_path"] and job["write_path"] not in policy["writable_roots"]:
        return "policy_blocked_path"
    return "allowed"

for job in requests:
    print(job["id"], "->", check(job))

assert check(requests[0]) == "allowed"
assert check(requests[1]) == "policy_blocked_network"
