#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date


def deletion_eligible(record: dict, current_day: int) -> bool:
    created = int(record["created_day"])
    retention = int(record["retention_days"])
    if current_day < created or retention < 0:
        raise ValueError("invalid retention timeline")
    if bool(record.get("legal_hold")):
        return False
    return current_day - created >= retention


def access_allowed(classification: str, role: str) -> bool:
    policy = {
        "public":{"reader","analyst","admin"},
        "internal":{"analyst","admin"},
        "restricted":{"admin"},
    }
    if classification not in policy:
        raise ValueError("unknown classification")
    return role in policy[classification]


def _valid_iso_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return False
    return parsed.isoformat() == value


def _required_ids(values: list[str]) -> tuple[set[str], int]:
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
    artifact_required = (
        "artifact_id",
        "artifact",
        "revision",
        "source",
        "license_or_terms",
        "review_evidence",
    )
    obligation_required = (
        "requirement_id",
        "requirement",
        "owner",
        "evidence",
        "reviewed_date",
    )

    required_artifact_ids, artifact_policy_violations = _required_ids(required_artifacts)
    required_obligation_ids, obligation_policy_violations = _required_ids(required_obligations)

    artifact_ids = [
        str(row.get("artifact_id", "")).strip()
        for row in artifacts
        if isinstance(row, dict)
    ]
    observed_artifacts = {value for value in artifact_ids if value}
    artifact_violations = artifact_policy_violations + sum(
        not (
            isinstance(row, dict)
            and all(str(row.get(key, "")).strip() for key in artifact_required)
            and row.get("terms_reviewed") is True
        )
        for row in artifacts
    )
    artifact_violations += len(artifact_ids) - len(observed_artifacts)
    artifact_violations += len(required_artifact_ids - observed_artifacts)

    obligation_ids = [
        str(row.get("requirement_id", "")).strip()
        for row in obligations
        if isinstance(row, dict)
    ]
    observed_obligations = {value for value in obligation_ids if value}
    governance_violations = obligation_policy_violations + sum(
        not (
            isinstance(row, dict)
            and isinstance(row.get("applicable"), bool)
            and all(str(row.get(key, "")).strip() for key in obligation_required)
            and _valid_iso_date(row.get("reviewed_date"))
        )
        for row in obligations
    )
    governance_violations += len(obligation_ids) - len(observed_obligations)
    governance_violations += len(required_obligation_ids - observed_obligations)

    return {
        "artifact_evidence_violations": int(artifact_violations),
        "governance_evidence_violations": int(governance_violations),
    }


REQUIRED_ARTIFACTS = ["base-model", "application-code"]
REQUIRED_GOVERNANCE = ["external-obligations-review", "scope-review"]

ARTIFACT_EVIDENCE = [
    {
        "artifact_id":"base-model",
        "artifact":"example-base-model",
        "revision":"reviewed-revision",
        "source":"approved artifact registry",
        "license_or_terms":"example-model-license-v2",
        "terms_reviewed":True,
        "review_evidence":"model-terms-review-17",
    },
    {
        "artifact_id":"application-code",
        "artifact":"application-code",
        "revision":"reviewed-commit",
        "source":"course repository",
        "license_or_terms":"repository license and dependency terms inventory",
        "terms_reviewed":True,
        "review_evidence":"dependency-and-license-review-22",
    },
]

GOVERNANCE_OBLIGATIONS = [
    {
        "requirement_id":"external-obligations-review",
        "requirement":"document applicable external obligations before release",
        "applicable":True,
        "owner":"compliance-review",
        "evidence":"governance-review-17",
        "reviewed_date":"2026-10-02",
    },
    {
        "requirement_id":"scope-review",
        "requirement":"record why a non-applicable obligation is out of scope",
        "applicable":False,
        "owner":"compliance-review",
        "evidence":"role-and-scope review recorded",
        "reviewed_date":"2026-10-02",
    },
]


if __name__ == "__main__":
    current_day = 10
    record = {"created_day":0,"retention_days":30,"legal_hold":False}
    evidence = evidence_summary(
        ARTIFACT_EVIDENCE,
        GOVERNANCE_OBLIGATIONS,
        REQUIRED_ARTIFACTS,
        REQUIRED_GOVERNANCE,
    )
    print(json.dumps({
        "current_day": current_day,
        "deletion_eligible": deletion_eligible(record, current_day),
        "restricted_analyst_access": access_allowed("restricted","analyst"),
        **evidence,
        "release_evidence_complete": (
            evidence["artifact_evidence_violations"] == 0
            and evidence["governance_evidence_violations"] == 0
        ),
    }, sort_keys=True))
