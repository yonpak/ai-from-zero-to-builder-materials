#!/usr/bin/env python3
from __future__ import annotations

import json
import math

VALID_CONCLUSIONS = {
    "confirmed_in_scope",
    "partially_reproduced",
    "not_reproduced",
    "inconclusive",
}
VALID_RELATIONS = {
    "candidate_gt_baseline",
    "candidate_gte_baseline",
    "candidate_lt_baseline",
    "candidate_lte_baseline",
    "candidate_eq_baseline",
}


def is_finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if isinstance(value, int):
        return True
    return math.isfinite(value)


def relation_holds(relation: str, baseline: float, candidate: float) -> bool:
    if relation == "candidate_gt_baseline":
        return candidate > baseline
    if relation == "candidate_gte_baseline":
        return candidate >= baseline
    if relation == "candidate_lt_baseline":
        return candidate < baseline
    if relation == "candidate_lte_baseline":
        return candidate <= baseline
    if relation == "candidate_eq_baseline":
        return candidate == baseline
    return False


def record_problems(record: dict) -> list[str]:
    required = (
        "claim",
        "environment",
        "seed_policy",
        "baseline",
        "candidate",
        "expected_relation",
        "conclusion",
    )
    problems = [
        f"missing {key}"
        for key in required
        if key not in record or record[key] in ("", None)
    ]

    conclusion = record.get("conclusion")
    if conclusion and conclusion not in VALID_CONCLUSIONS:
        problems.append(f"conclusion {conclusion!r} is not one of {sorted(VALID_CONCLUSIONS)}")

    relation = record.get("expected_relation")
    if relation and relation not in VALID_RELATIONS:
        problems.append(f"expected_relation {relation!r} is not supported")

    env = record.get("environment")
    if env and (not isinstance(env, dict) or not env.get("python")):
        problems.append("environment must record the python version")

    baseline = record.get("baseline")
    candidate = record.get("candidate")
    if baseline is not None and not is_finite_number(baseline):
        problems.append("baseline must be a finite number")
    if candidate is not None and not is_finite_number(candidate):
        problems.append("candidate must be a finite number")

    if (
        not problems
        and relation in VALID_RELATIONS
        and conclusion in VALID_CONCLUSIONS
    ):
        supports = relation_holds(relation, baseline, candidate)
        if conclusion in {"confirmed_in_scope", "partially_reproduced"} and not supports:
            problems.append("conclusion claims support but the expected relation did not hold")
        if conclusion == "not_reproduced" and supports:
            problems.append("not_reproduced conflicts with a satisfied expected relation")

    return problems


def validate_record(record: dict) -> bool:
    return not record_problems(record)


RECORD = {
    "claim":"candidate improves the measured score over baseline in this reduced setup",
    "environment":{"python":"3.11","platform":"cpu"},
    "seed_policy":"fixed seed 13",
    "baseline":0.72,
    "candidate":0.78,
    "expected_relation":"candidate_gt_baseline",
    "conclusion":"partially_reproduced",
}

if __name__ == "__main__":
    print(json.dumps({
        "record_valid": validate_record(RECORD),
        "expected_relation": RECORD["expected_relation"],
        "conclusion": RECORD["conclusion"],
        "problems": record_problems(RECORD),
    }, sort_keys=True))
