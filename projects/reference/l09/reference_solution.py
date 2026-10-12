"""Reference reduced-path implementation for p09-evidence-rag."""

import re

REQUIRED_TOP_LEVEL = {
    "project_id",
    "corpus_snapshot_id",
    "chunker_version",
    "retriever_version",
    "prompt_version",
    "generator_id",
    "evaluator_version",
    "source_catalog",
    "cases",
    "metrics",
    "release_rule",
    "release_passed",
    "debug_record",
    "limitations",
}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(text).lower()))


def token_overlap(query: str, text: str) -> int:
    return len(_words(query) & _words(text))


def eligible_source_ids(source_catalog: dict, tenant_id: str) -> list[str]:
    if not isinstance(source_catalog, dict):
        raise ValueError("source_catalog must be a dict")
    return sorted(
        source_id
        for source_id, record in source_catalog.items()
        if isinstance(record, dict)
        and record.get("tenant_id") == tenant_id
        and record.get("active") is True
    )


def retrieve(query: str, source_catalog: dict, tenant_id: str, k: int = 2) -> list[str]:
    if not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    eligible = eligible_source_ids(source_catalog, tenant_id)
    ranked = sorted(
        eligible,
        key=lambda source_id: (
            -token_overlap(query, source_catalog[source_id]["text"]),
            source_id,
        ),
    )
    return ranked[: min(k, len(ranked))]


def validate_grounded_output(output: dict, supplied_source_ids: list[str]) -> None:
    if not isinstance(output, dict):
        raise ValueError("output must be an object")
    if set(output) != {"answer", "supported", "source_id"}:
        raise ValueError("output must contain exactly answer, supported, source_id")
    if type(output["supported"]) is not bool:
        raise ValueError("supported must be bool")
    supplied = set(supplied_source_ids)
    if output["supported"]:
        if not isinstance(output["answer"], str) or not output["answer"].strip():
            raise ValueError("supported output needs a non-empty answer")
        if not isinstance(output["source_id"], str) or output["source_id"] not in supplied:
            raise ValueError("supported output must cite a supplied source")
    else:
        if output["answer"] is not None or output["source_id"] is not None:
            raise ValueError("unsupported output must abstain with null answer/source")


def _recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    relevant = set(relevant_ids)
    if not relevant:
        return 1.0
    found = relevant & set(retrieved_ids[:k])
    return len(found) / len(relevant)


def _grounded_case_pass(case: dict) -> bool:
    output = case["output"]
    return (
        output["supported"] is case["expected_supported"]
        and output["answer"] == case["expected_answer"]
    )


def _release(metrics: dict, rule: dict) -> bool:
    return (
        metrics["recall_at_2"] >= rule["min_recall_at_2"]
        and metrics["grounded_accuracy"] >= rule["min_grounded_accuracy"]
        and metrics["unauthorized_exposure_count"] <= rule["max_unauthorized_exposure"]
    )


def validate_run(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("run must be an object")
    missing = REQUIRED_TOP_LEVEL - data.keys()
    if missing:
        raise ValueError("missing: " + ", ".join(sorted(missing)))

    for key in [
        "project_id",
        "corpus_snapshot_id",
        "chunker_version",
        "retriever_version",
        "prompt_version",
        "generator_id",
        "evaluator_version",
    ]:
        if not str(data[key]).strip():
            raise ValueError(f"{key} must be non-empty")

    catalog = data["source_catalog"]
    if not isinstance(catalog, dict) or not catalog:
        raise ValueError("source_catalog must be a non-empty object")
    for source_id, record in catalog.items():
        if not str(source_id).strip() or not isinstance(record, dict):
            raise ValueError("invalid source record")
        if not str(record.get("text", "")).strip():
            raise ValueError(f"{source_id}: text must be non-empty")
        if not str(record.get("tenant_id", "")).strip():
            raise ValueError(f"{source_id}: tenant_id must be non-empty")
        if type(record.get("active")) is not bool:
            raise ValueError(f"{source_id}: active must be bool")

    cases = data["cases"]
    if not isinstance(cases, list) or len(cases) < 4:
        raise ValueError("at least four fixed cases are required")

    recalls = []
    grounded_passes = 0
    unauthorized_exposures = 0
    seen_ids = set()

    for case in cases:
        case_id = str(case.get("id", "")).strip()
        if not case_id or case_id in seen_ids:
            raise ValueError("case IDs must be non-empty and unique")
        seen_ids.add(case_id)
        tenant_id = str(case.get("tenant_id", "")).strip()
        query = str(case.get("query", "")).strip()
        if not tenant_id or not query:
            raise ValueError(f"{case_id}: tenant_id and query are required")

        relevant = case.get("relevant_source_ids")
        retrieved = case.get("retrieved_ids")
        supplied = case.get("supplied_source_ids")
        if not all(isinstance(x, list) for x in [relevant, retrieved, supplied]):
            raise ValueError(f"{case_id}: relevant/retrieved/supplied IDs must be lists")
        if any(source_id not in catalog for source_id in relevant + retrieved + supplied):
            raise ValueError(f"{case_id}: unknown source ID")

        eligible = set(eligible_source_ids(catalog, tenant_id))
        if any(source_id not in eligible for source_id in relevant):
            raise ValueError(f"{case_id}: relevant labels must refer to eligible evidence")
        bad_retrieved = [source_id for source_id in retrieved if source_id not in eligible]
        bad_supplied = [source_id for source_id in supplied if source_id not in eligible]
        unauthorized_exposures += len(bad_retrieved) + len(bad_supplied)
        if bad_retrieved or bad_supplied:
            raise ValueError(
                f"{case_id}: unauthorized or inactive evidence crossed the retrieval boundary"
            )

        if not set(supplied).issubset(set(retrieved)):
            raise ValueError(f"{case_id}: supplied sources must come from retrieved sources")

        validate_grounded_output(case.get("output"), supplied)

        if type(case.get("expected_supported")) is not bool:
            raise ValueError(f"{case_id}: expected_supported must be bool")

        recalls.append(_recall_at_k(retrieved, relevant, 2))
        grounded_passes += int(_grounded_case_pass(case))

    computed_metrics = {
        "recall_at_2": sum(recalls) / len(recalls),
        "grounded_accuracy": grounded_passes / len(cases),
        "unauthorized_exposure_count": unauthorized_exposures,
    }
    metrics = data["metrics"]
    for key, value in computed_metrics.items():
        if metrics.get(key) != value:
            raise ValueError(f"metrics.{key} does not match recomputed value")

    rule = data["release_rule"]
    for key in ["min_recall_at_2", "min_grounded_accuracy"]:
        value = rule.get(key)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"release_rule.{key} must be in [0,1]")
    if not isinstance(rule.get("max_unauthorized_exposure"), int) or rule["max_unauthorized_exposure"] < 0:
        raise ValueError("max_unauthorized_exposure must be non-negative int")

    expected_release = _release(metrics, rule)
    if data["release_passed"] is not expected_release:
        raise ValueError("release_passed does not match the declared rule")

    debug = data["debug_record"]
    for key in ["failure", "evidence", "hypothesis", "fix", "result"]:
        if not str(debug.get(key, "")).strip():
            raise ValueError(f"debug_record.{key} must be non-empty")
    if not str(data["limitations"]).strip():
        raise ValueError("limitations must be non-empty")
