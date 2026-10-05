from __future__ import annotations

"""Machine-checkable contract for the fixed Level 15 real-RAG cases.

The model produces only a structured claim and explicit source IDs. After those
values pass deterministic checks, application code renders the user-facing
answer from the verified data. This prevents prose and machine state from
silently contradicting each other.
"""

CANONICAL_CORPUS = [
    {"id": "D1", "text": "XR-4172 factory reset: hold the rear button for 10 seconds."},
    {"id": "D2", "text": "The XR-4100 battery normally lasts about eight hours."},
    {"id": "D3", "text": "Warranty coverage for XR-4172 is 18 months from purchase."},
    {"id": "D4", "text": "Resetting a device does not extend or renew its warranty."},
]
_CANONICAL_BY_ID = {row["id"]: row for row in CANONICAL_CORPUS}


REAL_RAG_CASE_SPECS = {
    "warranty-length": {
        "query": "How long is the XR-4172 warranty?",
        "expected_source": "D3",
        "expected_claim": {"warranty_months": 18},
    },
    "factory-reset": {
        "query": "How do I factory reset the XR-4172?",
        "expected_source": "D1",
        "expected_claim": {
            "action": "hold",
            "control": "rear_button",
            "seconds": 10,
        },
    },
    "reset-warranty": {
        "query": "Does resetting the XR-4172 renew its warranty?",
        "expected_source": "D4",
        "expected_claim": {"reset_changes_warranty": False},
    },
}


def _exact_scalar(actual: object, expected: object) -> bool:
    if isinstance(expected, bool):
        return type(actual) is bool and actual is expected
    if isinstance(expected, int):
        return type(actual) is int and actual == expected
    if isinstance(expected, str):
        return type(actual) is str and actual == expected
    return type(actual) is type(expected) and actual == expected


def claim_matches(case_id: str, claim: object) -> bool:
    spec = REAL_RAG_CASE_SPECS.get(case_id)
    if spec is None or not isinstance(claim, dict):
        return False
    expected = spec["expected_claim"]
    if set(claim) != set(expected):
        return False
    return all(_exact_scalar(claim[key], expected[key]) for key in expected)


def normalize_source_ids(value: object) -> list[str] | None:
    if not isinstance(value, list) or not value:
        return None
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            return None
        source_id = item.strip()
        if source_id in normalized:
            return None
        normalized.append(source_id)
    return normalized


def evaluate_structured_case(
    case_id: str,
    retrieved_ids: list[str],
    claim: object,
    source_ids: object,
) -> dict[str, bool]:
    spec = REAL_RAG_CASE_SPECS.get(case_id)
    if spec is None:
        raise ValueError(f"unknown real-RAG case: {case_id}")

    expected_source = spec["expected_source"]
    retrieval_ok = expected_source in retrieved_ids

    normalized_sources = normalize_source_ids(source_ids)
    source_ids_ok = (
        normalized_sources == [expected_source]
        and expected_source in retrieved_ids
    )

    claim_ok = claim_matches(case_id, claim)
    return {
        "retrieval_ok": retrieval_ok,
        "source_ids_ok": source_ids_ok,
        "claim_ok": claim_ok,
        "passed": retrieval_ok and source_ids_ok and claim_ok,
    }


def render_verified_answer(
    case_id: str,
    claim: object,
    source_ids: object,
) -> str:
    spec = REAL_RAG_CASE_SPECS.get(case_id)
    if spec is None:
        raise ValueError(f"unknown real-RAG case: {case_id}")
    if not claim_matches(case_id, claim):
        raise ValueError(f"cannot render unverified claim for {case_id}")
    normalized_sources = normalize_source_ids(source_ids)
    if normalized_sources != [spec["expected_source"]]:
        raise ValueError(f"cannot render unverified sources for {case_id}")

    source = normalized_sources[0]
    if case_id == "warranty-length":
        return f"The XR-4172 warranty is {claim['warranty_months']} months. [{source}]"
    if case_id == "factory-reset":
        return f"Hold the rear button for {claim['seconds']} seconds. [{source}]"
    if case_id == "reset-warranty":
        return f"Resetting the XR-4172 does not renew or extend its warranty. [{source}]"
    raise ValueError(f"unknown real-RAG case: {case_id}")
