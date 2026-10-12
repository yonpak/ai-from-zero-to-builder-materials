#!/usr/bin/env python3
"""Reference answer for L12.05."""

from pathlib import PurePosixPath

PROFILE = {
    "write_root": PurePosixPath("/workspace/task"),
    "network_hosts": {"inventory.internal"},
    "max_memory_mb": 256,
}


def allowed(request, profile=PROFILE):
    path_ok = request["path"].is_relative_to(profile["write_root"])
    host_ok = request["host"] in profile["network_hosts"]
    memory_ok = request["memory_mb"] <= profile["max_memory_mb"]
    return path_ok and host_ok and memory_ok


good = {"path": PurePosixPath("/workspace/task/report.txt"), "host": "inventory.internal", "memory_mb": 128}
assert allowed(good)
assert not allowed({**good, "path": PurePosixPath("/etc/passwd")})
assert not allowed({**good, "host": "example.com"})
assert not allowed({**good, "memory_mb": 257})
assert allowed({**good, "memory_mb": 256})
print("PASS: L12.05 reference answer enforces path, host, and memory boundaries")
