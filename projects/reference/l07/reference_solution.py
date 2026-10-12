"""Reference reduced-path implementation for p07-reliable-llm-workflow."""

import math
import re

REQUIRED_RUN_FIELDS = {
    "workflow_id",
    "model_id",
    "prompt_version",
    "decoding",
    "source_catalog",
    "cases",
    "debug_record",
    "limitations",
}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(text).lower()))


def word_overlap(query: str, text: str) -> int:
    return len(_words(query) & _words(text))


def retrieve(query: str, documents: dict[str, str], k: int = 1) -> list[str]:
    if not isinstance(documents, dict) or not documents:
        raise ValueError("documents must be a non-empty dict")
    if not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    ranked = sorted(
        documents,
        key=lambda doc_id: (-word_overlap(query, documents[doc_id]), doc_id),
    )
    return ranked[: min(k, len(ranked))]


def validate_model_output(output: dict, supplied_source_ids: list[str]) -> None:
    if not isinstance(output, dict):
        raise ValueError("output must be a dict")
    if set(output) != {"answer", "supported", "source_id"}:
        raise ValueError("output must contain exactly answer, supported, source_id")
    if type(output["supported"]) is not bool:
        raise ValueError("supported must be a bool")
    allowed = set(supplied_source_ids)
    if output["supported"]:
        if not isinstance(output["answer"], str) or not output["answer"].strip():
            raise ValueError("supported output needs a non-empty answer")
        if not isinstance(output["source_id"], str) or output["source_id"] not in allowed:
            raise ValueError("supported output must cite a supplied source")
    else:
        if output["answer"] is not None or output["source_id"] is not None:
            raise ValueError("unsupported output must abstain with null answer/source")


def evaluate_cases(cases: list[dict]) -> tuple[int, list[str]]:
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")
    passed = 0
    failed = []
    for case in cases:
        case_id = str(case.get("id", "")).strip()
        if not case_id:
            raise ValueError("each case needs an id")
        output = case.get("output")
        supplied = case.get("supplied_source_ids")
        if not isinstance(supplied, list):
            raise ValueError("each case needs supplied_source_ids")
        try:
            validate_model_output(output, supplied)
            correct = (
                output["supported"] is case.get("expected_supported")
                and output["answer"] == case.get("expected_answer")
            )
        except ValueError:
            correct = False
        if correct:
            passed += 1
        else:
            failed.append(case_id)
    return passed, failed


def validate_run(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("run data must be a dict")
    missing = REQUIRED_RUN_FIELDS - data.keys()
    if missing:
        raise ValueError("missing: " + ", ".join(sorted(missing)))
    for key in ("workflow_id", "model_id", "prompt_version"):
        if not str(data[key]).strip():
            raise ValueError(f"{key} must be non-empty")
    if not isinstance(data["decoding"], dict) or not str(data["decoding"].get("mode", "")).strip():
        raise ValueError("decoding needs a mode")
    catalog = data["source_catalog"]
    if not isinstance(catalog, dict) or not catalog:
        raise ValueError("source_catalog must be a non-empty dict")
    if not all(isinstance(k, str) and k and isinstance(v, str) and v.strip() for k, v in catalog.items()):
        raise ValueError("source_catalog entries must be non-empty text")
    cases = data["cases"]
    if not isinstance(cases, list) or len(cases) < 4:
        raise ValueError("at least four evaluation cases are required")
    ids = []
    for case in cases:
        case_id = str(case.get("id", "")).strip()
        if not case_id:
            raise ValueError("each case needs an id")
        ids.append(case_id)
        if not str(case.get("query", "")).strip():
            raise ValueError("each case needs a query")
        supplied = case.get("supplied_source_ids")
        if not isinstance(supplied, list) or any(source_id not in catalog for source_id in supplied):
            raise ValueError("case references an unknown supplied source")
        if type(case.get("expected_supported")) is not bool:
            raise ValueError("expected_supported must be bool")
        validate_model_output(case.get("output"), supplied)
    if len(set(ids)) != len(ids):
        raise ValueError("case ids must be unique")
    debug = data["debug_record"]
    if not isinstance(debug, dict) or any(
        not str(debug.get(k, "")).strip()
        for k in ["failure", "evidence", "hypothesis", "fix", "result"]
    ):
        raise ValueError("debug_record needs failure/evidence/hypothesis/fix/result")
    if not str(data["limitations"]).strip():
        raise ValueError("limitations must be non-empty")
