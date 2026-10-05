#!/usr/bin/env python3
"""Validate citation identity, factual support, and citation coverage separately."""

from __future__ import annotations

import argparse

EVIDENCE = {
    "policy-7#03": {"warranty_months": 18},
    "manual-4#02": {"battery_hours": 10},
}

FIXTURES = {
    "ok": [
        {"claim": "Warranty is 18 months", "source_id": "policy-7#03", "field": "warranty_months", "value": 18},
        {"claim": "Battery runtime is 10 hours", "source_id": "manual-4#02", "field": "battery_hours", "value": 10},
    ],
    "unsupplied": [
        {"claim": "Warranty is 18 months", "source_id": "manual-9#99", "field": "warranty_months", "value": 18},
        {"claim": "Battery runtime is 10 hours", "source_id": "manual-4#02", "field": "battery_hours", "value": 10},
    ],
    "unsupported": [
        {"claim": "Warranty is 24 months", "source_id": "policy-7#03", "field": "warranty_months", "value": 24},
        {"claim": "Battery runtime is 10 hours", "source_id": "manual-4#02", "field": "battery_hours", "value": 10},
    ],
    "uncited": [
        {"claim": "Warranty is 18 months", "source_id": "policy-7#03", "field": "warranty_months", "value": 18},
        {"claim": "Battery runtime is 10 hours", "source_id": None, "field": "battery_hours", "value": 10},
    ],
}


def validate(claims: list[dict]) -> tuple[list[tuple], list[tuple], int]:
    identity_failures = []
    support_failures = []
    cited = 0

    for item in claims:
        source_id = item["source_id"]
        if source_id is None:
            continue
        cited += 1
        if source_id not in EVIDENCE:
            identity_failures.append((item["claim"], source_id))
            continue
        source = EVIDENCE[source_id]
        if source.get(item["field"]) != item["value"]:
            support_failures.append((item["claim"], source_id))

    return identity_failures, support_failures, cited


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", choices=FIXTURES, default="ok")
    args = parser.parse_args()

    claims = FIXTURES[args.fixture]
    identity_failures, support_failures, cited = validate(claims)
    print("identity_failures:", identity_failures)
    print("support_failures:", support_failures)
    print(f"citation_coverage: {cited}/{len(claims)}")

    if identity_failures or support_failures or cited != len(claims):
        print("REJECT: citation check")
        raise SystemExit(1)

    print("PASS: citation check")


if __name__ == "__main__":
    main()
