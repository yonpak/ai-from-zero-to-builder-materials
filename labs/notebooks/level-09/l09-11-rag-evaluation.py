#!/usr/bin/env python3
"""Evaluate retrieval separately from answer correctness and grounding."""

from __future__ import annotations

import argparse

CASES = [
    {"id": "q1-warranty", "relevant": "policy-7#03", "retrieved": ["policy-7#03", "faq-2#11", "manual-4#02"], "answer_correct": True, "answer_supported": True},
    {"id": "q2-battery", "relevant": "manual-4#02", "retrieved": ["faq-2#11", "manual-4#02", "policy-7#03"], "answer_correct": True, "answer_supported": True},
    {"id": "q3-return", "relevant": "faq-2#11", "retrieved": ["manual-4#02", "policy-7#03", "faq-2#11"], "answer_correct": True, "answer_supported": False},
    {"id": "q4-weight", "relevant": "spec-1#05", "retrieved": ["manual-4#02", "faq-2#11", "policy-7#03"], "answer_correct": True, "answer_supported": False},
    {"id": "q5-repair-fee", "relevant": None, "retrieved": ["faq-2#11", "policy-7#03", "manual-4#02"], "answer_correct": True, "answer_supported": False, "abstained": True},
]

K = 3


def retrieval_metrics(cases: list[dict]) -> dict:
    answerable = [case for case in cases if case["relevant"] is not None]
    hits = 0
    reciprocal = 0.0
    for case in answerable:
        top_k = case["retrieved"][:K]
        if case["relevant"] in top_k:
            hits += 1
            reciprocal += 1 / (top_k.index(case["relevant"]) + 1)
    return {
        f"recall@{K}": round(hits / len(answerable), 3),
        "MRR": round(reciprocal / len(answerable), 3),
    }


def answer_metrics(cases: list[dict]) -> dict:
    answerable = [case for case in cases if case["relevant"] is not None]
    missing = [case for case in cases if case["relevant"] is None]
    return {
        "answer_correct": round(sum(case["answer_correct"] for case in cases) / len(cases), 3),
        "grounded_support": round(sum(case["answer_supported"] for case in answerable) / len(answerable), 3),
        "missing_evidence_abstention": round(sum(case.get("abstained", False) for case in missing) / len(missing), 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--move-q2-lower", action="store_true")
    parser.add_argument("--break-q1-support", action="store_true")
    args = parser.parse_args()

    cases = [dict(case, retrieved=list(case["retrieved"])) for case in CASES]
    if args.move_q2_lower:
        cases[1]["retrieved"] = ["faq-2#11", "policy-7#03", "manual-4#02"]
    if args.break_q1_support:
        cases[0]["answer_supported"] = False

    print("retrieval metrics:", retrieval_metrics(cases))
    print("answer metrics:", answer_metrics(cases))
    q4 = next(case for case in cases if case["id"] == "q4-weight")
    if q4["answer_correct"] and q4["relevant"] not in q4["retrieved"][:K]:
        print("q4-weight: correct answer but unsupported by retrieved evidence")
    print("PASS: retrieval and answer metrics reported separately")


if __name__ == "__main__":
    main()
