#!/usr/bin/env python3
"""Trace a retrieval problem to the earliest broken boundary."""

from __future__ import annotations

BOUNDARIES = [
    "source_present",
    "chunk_created",
    "eligible",
    "query_preserves_intent",
    "candidate_retrieved",
    "inside_top_k",
    "reranker_preserves_candidate",
]

CASES = [
    {
        "name": "source-never-ingested",
        "states": [False, False, False, False, False, False, False],
        "expected": "source_present",
    },
    {
        "name": "bad-chunking",
        "states": [True, False, False, False, False, False, False],
        "expected": "chunk_created",
    },
    {
        "name": "permission-exclusion",
        "states": [True, True, False, False, False, False, False],
        "expected": "eligible",
    },
    {
        "name": "rewrite-lost-keyword",
        "states": [True, True, True, False, False, False, False],
        "expected": "query_preserves_intent",
    },
    {
        "name": "retriever-miss",
        "states": [True, True, True, True, False, False, False],
        "expected": "candidate_retrieved",
    },
    {
        "name": "top-k-cutoff",
        "states": [True, True, True, True, True, False, False],
        "expected": "inside_top_k",
    },
    {
        "name": "reranker-dropped-it",
        "states": [True, True, True, True, True, True, False],
        "expected": "reranker_preserves_candidate",
    },
]


def first_broken(states: list[bool]) -> str | None:
    for boundary, ok in zip(BOUNDARIES, states):
        if not ok:
            return boundary
    return None


for case in CASES:
    observed = first_broken(case["states"])
    print(f"{case['name']}: first broken boundary = {observed}")
    if observed != case["expected"]:
        raise SystemExit(
            f"trace mismatch for {case['name']}: expected {case['expected']}, got {observed}"
        )

print("PASS: every retrieval failure stops at the earliest broken boundary")
