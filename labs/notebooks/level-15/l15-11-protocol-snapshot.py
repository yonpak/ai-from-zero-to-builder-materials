#!/usr/bin/env python3
from __future__ import annotations
import json

PINNED = {"mcp":"2026-07-28","a2a":"1.0.0","reviewed":"2026-09-08"}

def snapshot_problems(snapshot: dict) -> list[str]:
    problems = [
        f"{key} is {snapshot.get(key)!r}, reviewed evidence covers {PINNED[key]!r}"
        for key in ("mcp", "a2a", "reviewed")
        if snapshot.get(key) != PINNED[key]
    ]
    if snapshot.get("authorization") != "local_policy":
        problems.append("authorization must stay with local policy")
    return problems


def validate_snapshot(snapshot: dict) -> bool:
    return not snapshot_problems(snapshot)


# The protocol versions this deployment actually uses.
SNAPSHOT = {"mcp": "2026-07-28", "a2a": "1.0.0", "reviewed": "2026-09-08", "authorization": "local_policy"}

if __name__ == "__main__":
    print(json.dumps({"snapshot": SNAPSHOT, "valid": validate_snapshot(SNAPSHOT),
                      "problems": snapshot_problems(SNAPSHOT)}, sort_keys=True))
