#!/usr/bin/env python3
from __future__ import annotations
import json, math, statistics, sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEFAULT_FIXTURE = REPO / "projects" / "tests" / "l15" / "fixtures" / "passing" / "capstone-run.json"
CONCLUSIONS = {"confirmed_in_scope", "partially_reproduced", "not_reproduced", "inconclusive"}
RELATIONS = {"candidate_gt_baseline", "candidate_gte_baseline", "candidate_lt_baseline", "candidate_lte_baseline", "candidate_eq_baseline"}

def iso(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None

def finite(value):
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and (isinstance(value, int) or math.isfinite(value))
    )

def relation_holds(relation, baseline, candidate):
    return {
        "candidate_gt_baseline": candidate > baseline,
        "candidate_gte_baseline": candidate >= baseline,
        "candidate_lt_baseline": candidate < baseline,
        "candidate_lte_baseline": candidate <= baseline,
        "candidate_eq_baseline": candidate == baseline,
    }.get(relation, False)

def reproduction_valid(record):
    required = ("claim", "environment", "seed_policy", "baseline", "candidate", "expected_relation", "conclusion")
    if any(key not in record or record[key] in ("", None) for key in required):
        return False
    if record["conclusion"] not in CONCLUSIONS or str(record["expected_relation"]) not in RELATIONS:
        return False
    if not isinstance(record["environment"], dict) or not str(record["environment"].get("python", "")).strip():
        return False
    if not finite(record["baseline"]) or not finite(record["candidate"]):
        return False
    supports = relation_holds(str(record["expected_relation"]), record["baseline"], record["candidate"])
    if record["conclusion"] in {"confirmed_in_scope", "partially_reproduced"}:
        return supports
    if record["conclusion"] == "not_reproduced":
        return not supports
    return True

def evidence_violations(rows, required_ids, id_key, required_fields, extra_check=lambda row: True):
    if not isinstance(required_ids, list) or not required_ids:
        required, policy_violations = set(), 1
    else:
        normalized = [str(value).strip() for value in required_ids]
        required = {value for value in normalized if value}
        policy_violations = int(len(required) != len(normalized) or not all(normalized))
    if not isinstance(rows, list):
        return policy_violations + 1 + len(required)
    ids = [str(row.get(id_key, "")).strip() for row in rows if isinstance(row, dict)]
    observed = {value for value in ids if value}
    invalid = sum(
        not (
            isinstance(row, dict)
            and all(str(row.get(key, "")).strip() for key in required_fields)
            and extra_check(row)
        )
        for row in rows
    )
    duplicates = len([value for value in ids if value]) - len(observed)
    return policy_violations + invalid + duplicates + len(required - observed)

def recompute(data):
    regression_cases = data["regression_cases"]
    ratings = data["human_ratings"]
    if not regression_cases or not ratings:
        raise ValueError("regression cases and human ratings required")

    scores = [int(row["score"]) for row in ratings]
    if any(score < 1 or score > 5 for score in scores):
        raise ValueError("human scores must be 1..5")
    by_case = {}
    for row in ratings:
        by_case.setdefault(str(row["case_id"]), []).append(int(row["score"]))

    authorization = data["policy"]["authorization"]
    unauthorized = sum(
        bool(row.get("executed"))
        and str(row.get("proposal", {}).get("action", ""))
        not in set(authorization.get(str(row.get("principal", {}).get("role", "")), []))
        for row in data["actions"]
    )

    current_day = int(data["policy"]["current_day"])
    retention = 0
    for row in data["records"]:
        created = int(row["created_day"])
        retention_days = int(row["retention_days"])
        if current_day < created or retention_days < 0:
            raise ValueError("invalid retention timeline")
        eligible = not bool(row.get("legal_hold")) and current_day - created >= retention_days
        retention += int(bool(row.get("retained")) and eligible)

    threat_failures = 0
    for row in data["threat_tests"]:
        if not str(row.get("category", "")).strip():
            raise ValueError("threat category required")
        threat_failures += int(
            row.get("severity") == "critical" and row.get("observed") != row.get("expected")
        )

    reviewed = iso(data["policy"]["frontier_reviewed_through"])
    if reviewed is None:
        raise ValueError("frontier_reviewed_through must be ISO YYYY-MM-DD")
    claim_fields = ("claim", "evidence_source", "system_version", "snapshot_date", "scope", "local_test")
    frontier = 0
    for row in data["frontier_claims"]:
        snapshot = iso(row.get("snapshot_date"))
        if (
            any(not str(row.get(key, "")).strip() for key in claim_fields)
            or snapshot is None
            or snapshot > reviewed
        ):
            frontier += 1

    return {
        "regression_success": round(
            sum(bool(row["passed"]) for row in regression_cases) / len(regression_cases), 4
        ),
        "critical_regressions": sum(
            bool(row.get("critical")) and not bool(row["passed"]) for row in regression_cases
        ),
        "human_mean_score": round(statistics.fmean(scores), 3),
        "high_disagreement_cases": sum(
            len(values) > 1 and max(values) - min(values) >= 3
            for values in by_case.values()
        ),
        "unauthorized_actions": unauthorized,
        "retention_violations": retention,
        "critical_threat_failures": threat_failures,
        "frontier_evidence_violations": frontier,
        "reproduction_evidence_violations": sum(
            not reproduction_valid(row) for row in data["reproductions"]
        ),
        "artifact_evidence_violations": evidence_violations(
            data["artifact_evidence"],
            data["policy"]["required_artifacts"],
            "artifact_id",
            ("artifact_id", "artifact", "revision", "source", "license_or_terms", "review_evidence"),
            lambda row: row.get("terms_reviewed") is True,
        ),
        "governance_evidence_violations": evidence_violations(
            data["governance_obligations"],
            data["policy"]["required_governance_requirements"],
            "requirement_id",
            ("requirement_id", "requirement", "owner", "evidence", "reviewed_date"),
            lambda row: isinstance(row.get("applicable"), bool)
            and iso(row.get("reviewed_date")) is not None,
        ),
    }

def validate(data):
    if data.get("project_id") != "p15-ai-product-capstone":
        raise ValueError("unexpected project_id")
    got = recompute(data)
    if got != data["metrics"]:
        raise ValueError(f"metrics mismatch: expected {got!r}")
    rule = data["release_rule"]
    release = (
        got["regression_success"] >= rule["min_regression_success"]
        and got["critical_regressions"] <= rule["max_critical_regressions"]
        and got["human_mean_score"] >= rule["min_human_mean_score"]
        and got["high_disagreement_cases"] <= rule["max_high_disagreement_cases"]
        and got["unauthorized_actions"] <= rule["max_unauthorized_actions"]
        and got["retention_violations"] <= rule["max_retention_violations"]
        and got["critical_threat_failures"] <= rule["max_critical_threat_failures"]
        and got["frontier_evidence_violations"] <= rule["max_frontier_evidence_violations"]
        and got["reproduction_evidence_violations"] <= rule["max_reproduction_evidence_violations"]
        and got["artifact_evidence_violations"] <= rule["max_artifact_evidence_violations"]
        and got["governance_evidence_violations"] <= rule["max_governance_evidence_violations"]
    )
    if data["release_passed"] is not release:
        raise ValueError("release_passed mismatch")
    if not release:
        raise ValueError("release rule failed")

def main():
    if len(sys.argv) > 2:
        raise SystemExit("usage: l15-13-capstone-check.py [CAPSTONE-RUN.json]")
    fixture = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_FIXTURE
    try:
        validate(json.loads(fixture.read_text(encoding="utf-8")))
    except (ValueError, AssertionError, KeyError, TypeError) as exc:
        raise SystemExit("FAIL: Level 15 integration trace: " + str(exc))
    print("PASS: Level 15 integration trace")

if __name__ == "__main__":
    main()
