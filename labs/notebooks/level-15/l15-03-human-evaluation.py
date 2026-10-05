#!/usr/bin/env python3
from __future__ import annotations
import json
import statistics


def judge_order_disagreements(results: list[dict]) -> int:
    by_case: dict[str, set[str]] = {}
    orders: dict[str, set[str]] = {}
    for row in results:
        case_id = str(row["case_id"])
        winner = str(row["winner"])
        order = str(row["order"])
        by_case.setdefault(case_id, set()).add(winner)
        orders.setdefault(case_id, set()).add(order)
    return sum(
        len(orders[case_id]) > 1 and len(winners) > 1
        for case_id, winners in by_case.items()
    )


def summarize(ratings: list[dict], judge_results: list[dict] | None = None) -> dict:
    if not ratings:
        raise ValueError("ratings required")
    values = [int(row["score"]) for row in ratings]
    if any(value < 1 or value > 5 for value in values):
        raise ValueError("scores must be 1..5")
    by_case: dict[str, list[int]] = {}
    for row in ratings:
        by_case.setdefault(row["case_id"], []).append(int(row["score"]))
    disagreement = sum((max(v) - min(v)) >= 3 for v in by_case.values() if len(v) > 1)
    result = {
        "mean_score": round(statistics.fmean(values), 3),
        "cases": len(by_case),
        "high_disagreement_cases": disagreement,
    }
    if judge_results is not None:
        result["judge_order_disagreements"] = judge_order_disagreements(judge_results)
    return result


RATINGS = [
    {"case_id":"a","reviewer":"r1","score":4},
    {"case_id":"a","reviewer":"r2","score":4},
    {"case_id":"a","reviewer":"r3","score":5},
    {"case_id":"b","reviewer":"r1","score":3},
    {"case_id":"b","reviewer":"r2","score":4},
    {"case_id":"b","reviewer":"r3","score":4},
]

# The same underlying candidates are judged in both presentation orders.
# A stable pairwise judge should still select candidate A in both rows.
JUDGE_RESULTS = [
    {"case_id":"pair-1","order":"A_then_B","winner":"A"},
    {"case_id":"pair-1","order":"B_then_A","winner":"A"},
]

if __name__ == "__main__":
    print(json.dumps(summarize(RATINGS, JUDGE_RESULTS), sort_keys=True))
