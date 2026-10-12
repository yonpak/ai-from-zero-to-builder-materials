#!/usr/bin/env python3
"""Reference answer for L15.02."""


def compare(baseline, candidate):
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
    failures_by_slice = {}
    for row in candidate:
        if not row["passed"]:
            failures_by_slice[row["slice"]] = failures_by_slice.get(row["slice"], 0) + 1

    return {
        "newly_failing": newly_failing,
        "fixed": fixed,
        "candidate_failures_by_slice": failures_by_slice,
    }


baseline = [
    {"id": "faq-1", "slice": "common", "passed": True},
    {"id": "auth-1", "slice": "authorization", "passed": True},
    {"id": "cite-1", "slice": "grounding", "passed": False},
]
candidate = [
    {"id": "faq-1", "slice": "common", "passed": True},
    {"id": "auth-1", "slice": "authorization", "passed": False},
    {"id": "cite-1", "slice": "grounding", "passed": True},
]
result = compare(baseline, candidate)
assert result == {
    "newly_failing": ["auth-1"],
    "fixed": ["cite-1"],
    "candidate_failures_by_slice": {"authorization": 1},
}
try:
    compare(baseline, candidate[:-1])
except ValueError:
    pass
else:
    raise AssertionError("mismatched case IDs must be rejected")
print("PASS: L15.02 reference answer validates case identity and reports regressions by slice")
