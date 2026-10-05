#!/usr/bin/env python3
from pathlib import PurePosixPath

profile={"write_root":PurePosixPath("/workspace/task"),"network_hosts":{"inventory.internal"},"max_memory_mb":256}
request={"path":PurePosixPath("/workspace/task/report.txt"),"host":"inventory.internal","memory_mb":128}

allowed_path=request["path"].is_relative_to(profile["write_root"])
allowed_host=request["host"] in profile["network_hosts"]
allowed_memory=request["memory_mb"]<=profile["max_memory_mb"]
print({"path":allowed_path,"network":allowed_host,"memory":allowed_memory})
assert allowed_path and allowed_host and allowed_memory
print("PASS: sandbox profile narrows reachable resources")
