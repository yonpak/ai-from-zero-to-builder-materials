#!/usr/bin/env python3
"""Learner exercise for L12.05: evaluate a sandbox policy."""

from pathlib import PurePosixPath

PROFILE = {
    "write_root": PurePosixPath("/workspace/task"),
    "network_hosts": {"inventory.internal"},
    "max_memory_mb": 256,
}


def allowed(request, profile=PROFILE):
    # TODO 1: allow writes only below write_root.
    # TODO 2: allow only listed network hosts.
    # TODO 3: enforce the memory ceiling.
    raise NotImplementedError("TODO: implement sandbox checks")


good = {"path": PurePosixPath("/workspace/task/report.txt"), "host": "inventory.internal", "memory_mb": 128}
bad_path = {**good, "path": PurePosixPath("/etc/passwd")}
bad_host = {**good, "host": "example.com"}
bad_memory = {**good, "memory_mb": 512}
assert allowed(good)
assert not allowed(bad_path)
assert not allowed(bad_host)
assert not allowed(bad_memory)
print("PASS: learner sandbox gate narrows path, network, and memory access")
