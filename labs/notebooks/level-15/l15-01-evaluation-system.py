#!/usr/bin/env python3
from __future__ import annotations
import json

def summarize(cases: list[dict], minimum_success: float = 0.8) -> dict:
    if not cases:
        raise ValueError("cases required")
    passed = sum(bool(row["passed"]) for row in cases)
    critical_failures = sum(bool(row.get("critical")) and not bool(row["passed"]) for row in cases)
    success = passed / len(cases)
    return {
        "case_success": round(success, 4),
        "critical_failures": critical_failures,
        "release_passed": success >= minimum_success and critical_failures == 0,
    }

CASES = [
    {"id": "common-1", "slice": "common", "passed": True, "critical": False},
    {"id": "common-2", "slice": "common", "passed": True, "critical": False},
    {"id": "common-3", "slice": "common", "passed": True, "critical": False},
    {"id": "common-4", "slice": "common", "passed": True, "critical": False},
    {"id": "common-5", "slice": "common", "passed": True, "critical": False},
    {"id": "common-6", "slice": "common", "passed": True, "critical": False},
    {"id": "format-1", "slice": "format", "passed": True, "critical": False},
    {"id": "format-2", "slice": "format", "passed": True, "critical": False},
    {"id": "format-3", "slice": "format", "passed": True, "critical": False},
    {"id": "auth-1", "slice": "authorization", "passed": True, "critical": True},
]
if __name__ == "__main__":
    print(json.dumps(summarize(CASES), sort_keys=True))
