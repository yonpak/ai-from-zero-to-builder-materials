#!/usr/bin/env python3
from __future__ import annotations
import json

def required_controls(permission: str) -> list[str]:
    if permission not in {"read", "write"}:
        raise ValueError("permission must be read or write")
    base = ["input_validation", "audit_evidence"]
    if permission == "write":
        base += ["authorization", "side_effect_confirmation"]
    return base

def map_risk(workflow: dict) -> dict:
    permission = workflow["permission"]
    controls = required_controls(permission)
    return {
        "asset": workflow["asset"],
        "permission": permission,
        "controls": controls,
        "residual_risk_review_required": permission == "write",
    }

if __name__ == "__main__":
    print(json.dumps(map_risk({"asset":"customer_record","permission":"read"}), sort_keys=True))
