from __future__ import annotations

import statistics
import math
from datetime import date

VALID_REPRODUCTION_CONCLUSIONS = {
    "confirmed_in_scope",
    "partially_reproduced",
    "not_reproduced",
    "inconclusive",
}
VALID_EXPECTED_RELATIONS = {
    "candidate_gt_baseline",
    "candidate_gte_baseline",
    "candidate_lt_baseline",
    "candidate_lte_baseline",
    "candidate_eq_baseline",
}

def _parse_iso_date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def regression_summary(cases: list[dict]) -> dict:
    if not cases:
        raise ValueError("regression cases required")
    passed = sum(bool(row["passed"]) for row in cases)
    critical = sum(bool(row.get("critical")) and not bool(row["passed"]) for row in cases)
    return {
        "regression_success": round(passed / len(cases), 4),
        "critical_regressions": critical,
    }


def human_review_summary(ratings: list[dict]) -> dict:
    if not ratings:
        raise ValueError("human ratings required")
    values = [int(row["score"]) for row in ratings]
    if any(score < 1 or score > 5 for score in values):
        raise ValueError("human scores must be 1..5")
    by_case: dict[str, list[int]] = {}
    for row in ratings:
        by_case.setdefault(str(row["case_id"]), []).append(int(row["score"]))
    disagreement = sum(
        len(scores) > 1 and max(scores) - min(scores) >= 3
        for scores in by_case.values()
    )
    return {
        "human_mean_score": round(statistics.fmean(values), 3),
        "high_disagreement_cases": disagreement,
    }


def authorize_action(principal: dict, proposal: dict, policy: dict) -> bool:
    role = str(principal.get("role", ""))
    action = str(proposal.get("action", ""))
    return action in set(policy.get(role, []))


def deletion_eligible(record: dict, current_day: int) -> bool:
    created = int(record["created_day"])
    retention = int(record["retention_days"])
    if current_day < created or retention < 0:
        raise ValueError("invalid retention timeline")
    if bool(record.get("legal_hold")):
        return False
    return current_day - created >= retention


def threat_summary(cases: list[dict]) -> dict:
    if not cases:
        raise ValueError("threat tests required")
    if any(not str(row.get("category", "")).strip() for row in cases):
        raise ValueError("threat category required")
    mismatches = [row for row in cases if row["observed"] != row["expected"]]
    critical = sum(row.get("severity") == "critical" for row in mismatches)
    return {
        "threat_test_mismatches": len(mismatches),
        "critical_threat_failures": critical,
    }


def frontier_claim_valid(claim: dict, reviewed_through: str) -> bool:
    required = (
        "claim",
        "evidence_source",
        "system_version",
        "snapshot_date",
        "scope",
        "local_test",
    )
    if any(not str(claim.get(key, "")).strip() for key in required):
        return False
    snapshot = _parse_iso_date(claim.get("snapshot_date"))
    reviewed = _parse_iso_date(reviewed_through)
    return snapshot is not None and reviewed is not None and snapshot <= reviewed


def _is_finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if isinstance(value, int):
        return True
    return math.isfinite(value)


def _relation_holds(relation: str, baseline: float, candidate: float) -> bool:
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


def reproduction_record_valid(record: dict) -> bool:
    required = (
        "claim",
        "environment",
        "seed_policy",
        "baseline",
        "candidate",
        "expected_relation",
        "conclusion",
    )
    if any(key not in record or record[key] in ("", None) for key in required):
        return False
    if record["conclusion"] not in VALID_REPRODUCTION_CONCLUSIONS:
        return False
    relation = str(record["expected_relation"])
    if relation not in VALID_EXPECTED_RELATIONS:
        return False
    if not isinstance(record["environment"], dict) or not str(
        record["environment"].get("python", "")
    ).strip():
        return False
    if not _is_finite_number(record["baseline"]) or not _is_finite_number(
        record["candidate"]
    ):
        return False

    supports_claim = _relation_holds(
        relation,
        record["baseline"],
        record["candidate"],
    )
    conclusion = record["conclusion"]
    if conclusion in {"confirmed_in_scope", "partially_reproduced"}:
        return supports_claim
    if conclusion == "not_reproduced":
        return not supports_claim
    return True


def _required_ids(values: object) -> tuple[set[str], int]:
    if not isinstance(values, list) or not values:
        return set(), 1
    ids = [str(value).strip() for value in values]
    invalid = sum(not value for value in ids)
    clean = [value for value in ids if value]
    duplicates = len(clean) - len(set(clean))
    return set(clean), invalid + duplicates


def evidence_summary(
    artifacts: list[dict],
    obligations: list[dict],
    required_artifacts: list[str],
    required_obligations: list[str],
) -> dict:
    artifact_required_fields = (
        "artifact_id",
        "artifact",
        "revision",
        "source",
        "license_or_terms",
        "review_evidence",
    )
    obligation_required_fields = (
        "requirement_id",
        "requirement",
        "owner",
        "evidence",
        "reviewed_date",
    )

    required_artifact_ids, artifact_policy_violations = _required_ids(required_artifacts)
    required_obligation_ids, obligation_policy_violations = _required_ids(required_obligations)

    artifact_rows = artifacts if isinstance(artifacts, list) else []
    artifact_ids = [
        str(row.get("artifact_id", "")).strip()
        for row in artifact_rows
        if isinstance(row, dict)
    ]
    observed_artifact_ids = {value for value in artifact_ids if value}
    artifact_invalid_rows = sum(
        not (
            isinstance(row, dict)
            and all(str(row.get(key, "")).strip() for key in artifact_required_fields)
            and row.get("terms_reviewed") is True
        )
        for row in artifact_rows
    )
    artifact_duplicates = len([value for value in artifact_ids if value]) - len(
        observed_artifact_ids
    )
    artifact_missing = len(required_artifact_ids - observed_artifact_ids)
    artifact_violations = (
        artifact_policy_violations
        + artifact_invalid_rows
        + artifact_duplicates
        + artifact_missing
    )
    if not isinstance(artifacts, list):
        artifact_violations += 1

    obligation_rows = obligations if isinstance(obligations, list) else []
    obligation_ids = [
        str(row.get("requirement_id", "")).strip()
        for row in obligation_rows
        if isinstance(row, dict)
    ]
    observed_obligation_ids = {value for value in obligation_ids if value}
    obligation_invalid_rows = sum(
        not (
            isinstance(row, dict)
            and isinstance(row.get("applicable"), bool)
            and all(str(row.get(key, "")).strip() for key in obligation_required_fields)
            and _parse_iso_date(row.get("reviewed_date")) is not None
        )
        for row in obligation_rows
    )
    obligation_duplicates = len([value for value in obligation_ids if value]) - len(
        observed_obligation_ids
    )
    obligation_missing = len(required_obligation_ids - observed_obligation_ids)
    governance_violations = (
        obligation_policy_violations
        + obligation_invalid_rows
        + obligation_duplicates
        + obligation_missing
    )
    if not isinstance(obligations, list):
        governance_violations += 1

    return {
        "artifact_evidence_violations": int(artifact_violations),
        "governance_evidence_violations": int(governance_violations),
    }


def _release_failures(metrics: dict, rule: dict) -> list[str]:
    checks = [
        ("regression_success", metrics["regression_success"] >= rule["min_regression_success"]),
        ("critical_regressions", metrics["critical_regressions"] <= rule["max_critical_regressions"]),
        ("human_mean_score", metrics["human_mean_score"] >= rule["min_human_mean_score"]),
        (
            "high_disagreement_cases",
            metrics["high_disagreement_cases"] <= rule["max_high_disagreement_cases"],
        ),
        ("unauthorized_actions", metrics["unauthorized_actions"] <= rule["max_unauthorized_actions"]),
        ("retention_violations", metrics["retention_violations"] <= rule["max_retention_violations"]),
        (
            "critical_threat_failures",
            metrics["critical_threat_failures"] <= rule["max_critical_threat_failures"],
        ),
        (
            "frontier_evidence_violations",
            metrics["frontier_evidence_violations"] <= rule["max_frontier_evidence_violations"],
        ),
        (
            "reproduction_evidence_violations",
            metrics["reproduction_evidence_violations"] <= rule["max_reproduction_evidence_violations"],
        ),
        (
            "artifact_evidence_violations",
            metrics["artifact_evidence_violations"] <= rule["max_artifact_evidence_violations"],
        ),
        (
            "governance_evidence_violations",
            metrics["governance_evidence_violations"] <= rule["max_governance_evidence_violations"],
        ),
    ]
    return [name for name, passed in checks if not passed]


def release_allowed(metrics: dict, rule: dict) -> bool:
    return not _release_failures(metrics, rule)


def _recompute_raw(data: dict) -> dict:
    regression = regression_summary(data["regression_cases"])
    human = human_review_summary(data["human_ratings"])
    threat = threat_summary(data["threat_tests"])
    evidence = evidence_summary(
        data["artifact_evidence"],
        data["governance_obligations"],
        data["policy"]["required_artifacts"],
        data["policy"]["required_governance_requirements"],
    )

    auth_policy = data["policy"]["authorization"]
    unauthorized = sum(
        bool(row.get("executed"))
        and not authorize_action(row["principal"], row["proposal"], auth_policy)
        for row in data["actions"]
    )

    current_day = int(data["policy"]["current_day"])
    retention = sum(
        bool(row.get("retained")) and deletion_eligible(row, current_day)
        for row in data["records"]
    )

    reviewed = data["policy"]["frontier_reviewed_through"]
    frontier = sum(not frontier_claim_valid(row, reviewed) for row in data["frontier_claims"])
    reproductions = sum(not reproduction_record_valid(row) for row in data["reproductions"])

    return {
        **regression,
        **human,
        "unauthorized_actions": unauthorized,
        "retention_violations": retention,
        "critical_threat_failures": threat["critical_threat_failures"],
        "frontier_evidence_violations": frontier,
        "reproduction_evidence_violations": reproductions,
        **evidence,
    }


def validate_run(data: dict) -> None:
    required = {
        "project_id",
        "policy",
        "regression_cases",
        "human_ratings",
        "actions",
        "records",
        "threat_tests",
        "frontier_claims",
        "reproductions",
        "artifact_evidence",
        "governance_obligations",
        "metrics",
        "release_rule",
        "release_passed",
    }
    missing = required - data.keys()
    if missing:
        raise ValueError("missing: " + ", ".join(sorted(missing)))
    if data["project_id"] != "p15-ai-product-capstone":
        raise ValueError("unexpected project_id")

    policy_required = {
        "authorization",
        "current_day",
        "frontier_reviewed_through",
        "required_artifacts",
        "required_governance_requirements",
    }
    policy_missing = policy_required - data["policy"].keys()
    if policy_missing:
        raise ValueError("policy missing: " + ", ".join(sorted(policy_missing)))
    if _parse_iso_date(data["policy"]["frontier_reviewed_through"]) is None:
        raise ValueError("frontier_reviewed_through must be ISO YYYY-MM-DD")

    got = _recompute_raw(data)
    if got != data["metrics"]:
        raise ValueError(f"metrics mismatch: expected {got!r}")

    failures = _release_failures(got, data["release_rule"])
    release = not failures
    if data["release_passed"] is not release:
        raise ValueError("release_passed mismatch")
    if failures:
        raise ValueError("release rule failed: " + ", ".join(failures))
