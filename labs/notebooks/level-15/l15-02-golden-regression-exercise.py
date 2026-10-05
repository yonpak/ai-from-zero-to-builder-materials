#!/usr/bin/env python3
"""Learner exercise for L15.02: compare a golden regression set."""

BASELINE = [
    {"id": "faq-1", "slice": "common", "passed": True},
    {"id": "auth-1", "slice": "authorization", "passed": True},
    {"id": "cite-1", "slice": "grounding", "passed": False},
]
CANDIDATE = [
    {"id": "faq-1", "slice": "common", "passed": True},
    {"id": "auth-1", "slice": "authorization", "passed": False},
    {"id": "cite-1", "slice": "grounding", "passed": True},
]


def compare(baseline, candidate):
    # TODO 1: require identical case IDs.
    # TODO 2: compute newly failing and fixed case IDs.
    # TODO 3: count candidate failures by slice.
    raise NotImplementedError("TODO: implement regression comparison")


result = compare(BASELINE, CANDIDATE)
assert result["newly_failing"] == ["auth-1"]
assert result["fixed"] == ["cite-1"]
assert result["candidate_failures_by_slice"] == {"authorization": 1}
print("PASS: learner regression comparison reports case-level changes and slices")
