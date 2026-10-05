#!/usr/bin/env python3
from __future__ import annotations
import json

REQUIRED = ("asset", "boundary", "path", "control")

def validate_threats(threats: list[dict]) -> dict:
    if not threats:
        raise ValueError("threats required")
    incomplete = []
    for index, threat in enumerate(threats):
        if any(not str(threat.get(key, "")).strip() for key in REQUIRED):
            incomplete.append(index)
    return {"threats": len(threats), "incomplete": incomplete, "ready_for_test": not incomplete}

THREATS = [
    {
        "asset":"private_notes",
        "boundary":"retrieved_page -> tool_policy",
        "path":"untrusted text proposes private read",
        "control":"policy restricts collection before tool execution",
    }
]
if __name__ == "__main__":
    print(json.dumps(validate_threats(THREATS), sort_keys=True))
