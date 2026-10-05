#!/usr/bin/env python3
from __future__ import annotations
import json

def compare(baseline: list[dict], candidate: list[dict]) -> dict:
    before = {row["id"]: row for row in baseline}
    after = {row["id"]: row for row in candidate}
    if before.keys() != after.keys():
        raise ValueError("baseline and candidate case IDs must match")
    newly_failing = sorted(
        case_id for case_id in before
        if bool(before[case_id]["passed"]) and not bool(after[case_id]["passed"])
    )
    fixed = sorted(
        case_id for case_id in before
        if not bool(before[case_id]["passed"]) and bool(after[case_id]["passed"])
    )
    by_slice: dict[str, int] = {}
    for row in candidate:
        if not row["passed"]:
            by_slice[row["slice"]] = by_slice.get(row["slice"], 0) + 1
    rate = lambda rows: round(sum(bool(r["passed"]) for r in rows) / len(rows), 3)
    return {"baseline_pass_rate": rate(baseline), "candidate_pass_rate": rate(candidate),
            "newly_failing": newly_failing, "fixed": fixed, "candidate_failures_by_slice": by_slice}

BASELINE = [
    {"id":"faq-1","slice":"common","passed":True},
    {"id":"auth-1","slice":"authorization","passed":True},
    {"id":"cite-1","slice":"grounding","passed":False},
]
CANDIDATE = [
    {"id":"faq-1","slice":"common","passed":True},
    {"id":"auth-1","slice":"authorization","passed":True},
    {"id":"cite-1","slice":"grounding","passed":True},
]
if __name__ == "__main__":
    print(json.dumps(compare(BASELINE, CANDIDATE), sort_keys=True))
