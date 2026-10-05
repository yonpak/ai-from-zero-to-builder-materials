#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import date

REQUIRED = ("claim", "evidence_source", "system_version", "snapshot_date", "scope", "local_test")
REVIEW_DATE = "2026-09-26"


def missing_fields(claim: dict) -> list[str]:
    return [key for key in REQUIRED if not str(claim.get(key, "")).strip()]


def parse_iso_date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def validate_claim(claim: dict) -> bool:
    if missing_fields(claim):
        return False
    snapshot = parse_iso_date(claim.get("snapshot_date"))
    reviewed = parse_iso_date(REVIEW_DATE)
    return snapshot is not None and reviewed is not None and snapshot <= reviewed


def reasoning_result_valid(result: dict) -> bool:
    model_version = result.get("model_version")
    inference_budget = result.get("inference_budget")
    score = result.get("task_score")
    latency = result.get("latency_ms")
    unit_cost = result.get("unit_cost")
    return (
        bool(str(model_version or "").strip())
        and bool(str(inference_budget or "").strip())
        and isinstance(score, (int, float))
        and not isinstance(score, bool)
        and 0 <= float(score) <= 1
        and isinstance(latency, (int, float))
        and not isinstance(latency, bool)
        and float(latency) >= 0
        and isinstance(unit_cost, (int, float))
        and not isinstance(unit_cost, bool)
        and float(unit_cost) >= 0
    )


CLAIM = {
    "claim":"benchmark result may motivate a local product evaluation",
    "evidence_source":"reviewed benchmark report",
    "system_version":"example-v1",
    "snapshot_date":"2026-09-26",
    "scope":"reported benchmark conditions only",
    "local_test":"run product regression suite before adoption",
}

REASONING_RESULT = {
    "model_version":"example-reasoning-v1",
    "inference_budget":"medium",
    "task_score":0.82,
    "latency_ms":2400,
    "unit_cost":0.012,
}

if __name__ == "__main__":
    print(json.dumps({
        "claim_valid": validate_claim(CLAIM),
        "missing_fields": missing_fields(CLAIM),
        "snapshot": CLAIM.get("snapshot_date", ""),
        "reasoning_result_valid": reasoning_result_valid(REASONING_RESULT),
        "reasoning_budget": REASONING_RESULT.get("inference_budget", ""),
    }, sort_keys=True))
