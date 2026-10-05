"""Small runtime helpers for the optional Level 15 real-RAG exercise.

This module intentionally has no ML-library imports so the stage boundaries can
be regression-tested without downloading model weights.
"""

from __future__ import annotations

import math


class TrackedEmbedder:
    """Proxy that counts embedding calls only after they return successfully."""

    def __init__(self, model):
        self._model = model
        self.encode_calls = 0

    def encode(self, *args, **kwargs):
        result = self._model.encode(*args, **kwargs)
        self.encode_calls += 1
        return result

    def __getattr__(self, name):
        return getattr(self._model, name)


class TrackedGenerator:
    """Proxy that counts generation calls only after they return successfully."""

    def __init__(self, model):
        self._model = model
        self.generate_calls = 0

    def generate(self, *args, **kwargs):
        result = self._model.generate(*args, **kwargs)
        self.generate_calls += 1
        return result

    def __getattr__(self, name):
        return getattr(self._model, name)


def validate_hits(hits, corpus: list[dict], top_k: int) -> list[tuple[dict, float]]:
    if not isinstance(hits, list) or len(hits) != top_k:
        raise ValueError(f"retrieve() must return exactly {top_k} (document, score) pairs")

    supplied = {row["id"]: row for row in corpus}
    normalized: list[tuple[dict, float]] = []
    seen_ids: set[str] = set()
    for item in hits:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("each retrieval result must be a (document, score) pair")
        document, score = item
        if not isinstance(document, dict) or document != supplied.get(document.get("id")):
            raise ValueError("retrieved document must exactly match a supplied corpus row")
        source_id = document["id"]
        if source_id in seen_ids:
            raise ValueError("retrieved document IDs must be unique")
        if isinstance(score, bool):
            raise ValueError("retrieval score must be a finite number")
        try:
            numeric_score = float(score)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("retrieval score must be a finite number") from error
        if not math.isfinite(numeric_score):
            raise ValueError("retrieval score must be a finite number")
        seen_ids.add(source_id)
        normalized.append((dict(document), numeric_score))
    return normalized


def _serialized_hits(hits: list[tuple[dict, float]]) -> list[dict]:
    return [
        {
            "id": document["id"],
            "text": document["text"],
            "score": round(score, 6),
        }
        for document, score in hits
    ]


def _error_row(
    *,
    case: dict,
    hits: list[tuple[dict, float]],
    claim,
    source_ids,
    embedder_called: bool,
    generator_called: bool,
    stage: str,
    error: Exception,
    claim_contract,
) -> dict:
    retrieved_ids = [document["id"] for document, _ in hits]
    checks = claim_contract.evaluate_structured_case(
        case["id"],
        retrieved_ids,
        claim,
        source_ids,
    )
    return {
        "case_id": case["id"],
        "query": case["query"],
        "expected_claim": case["expected_claim"],
        "expected_source": case["expected_source"],
        "retrieved": _serialized_hits(hits),
        "claim": claim,
        "source_ids": source_ids,
        "checks": {
            "embedder_called": embedder_called,
            "generator_called": generator_called,
            "generation_status": "error" if stage == "generation" else "not_run",
            "structured_output_object_ok": False,
            "structured_output_shape_ok": False,
            "retrieval_contains_expected_source": checks["retrieval_ok"],
            "source_matches": checks["source_ids_ok"],
            "claim_matches": checks["claim_ok"],
        },
        "answer": None,
        "error": {
            "stage": stage,
            "type": type(error).__name__,
            "message": str(error),
        },
    }


def run_case(
    *,
    product,
    case: dict,
    corpus: list[dict],
    embedder,
    tokenizer,
    generator,
    device: str,
    top_k: int,
    max_new_tokens: int,
    claim_contract,
) -> dict:
    """Run retrieve -> ground -> generate while preserving completed-stage evidence."""

    embed_before = embedder.encode_calls
    generate_before = generator.generate_calls
    hits: list[tuple[dict, float]] = []
    claim = None
    source_ids = []

    try:
        hits = validate_hits(
            product.retrieve(embedder, corpus, case["query"], top_k),
            corpus,
            top_k,
        )
    except Exception as error:
        return _error_row(
            case=case,
            hits=[],
            claim=None,
            source_ids=[],
            embedder_called=embedder.encode_calls > embed_before,
            generator_called=generator.generate_calls > generate_before,
            stage="retrieval",
            error=error,
            claim_contract=claim_contract,
        )

    try:
        messages = product.build_grounded_messages(case["query"], hits)
    except Exception as error:
        return _error_row(
            case=case,
            hits=hits,
            claim=None,
            source_ids=[],
            embedder_called=embedder.encode_calls > embed_before,
            generator_called=generator.generate_calls > generate_before,
            stage="grounding",
            error=error,
            claim_contract=claim_contract,
        )

    try:
        generated = product.generate_grounded_claim(
            tokenizer,
            generator,
            device,
            messages,
            max_new_tokens,
        )
    except Exception as error:
        return _error_row(
            case=case,
            hits=hits,
            claim=None,
            source_ids=[],
            embedder_called=embedder.encode_calls > embed_before,
            generator_called=generator.generate_calls > generate_before,
            stage="generation",
            error=error,
            claim_contract=claim_contract,
        )

    structured_output_object_ok = isinstance(generated, dict)
    if structured_output_object_ok:
        claim = generated.get("claim")
        source_ids = generated.get("source_ids")
    else:
        claim = None
        source_ids = []

    retrieved_ids = [document["id"] for document, _ in hits]
    checks = claim_contract.evaluate_structured_case(
        case["id"],
        retrieved_ids,
        claim,
        source_ids,
    )
    embedder_called = embedder.encode_calls > embed_before
    generator_called = generator.generate_calls > generate_before
    mechanics_ok = embedder_called and generator_called
    shape_ok = isinstance(claim, dict) and isinstance(source_ids, list)
    answer = (
        claim_contract.render_verified_answer(case["id"], claim, source_ids)
        if mechanics_ok and checks["passed"]
        else None
    )

    return {
        "case_id": case["id"],
        "query": case["query"],
        "expected_claim": case["expected_claim"],
        "expected_source": case["expected_source"],
        "retrieved": _serialized_hits(hits),
        "claim": claim,
        "source_ids": source_ids,
        "checks": {
            "embedder_called": embedder_called,
            "generator_called": generator_called,
            "generation_status": "returned",
            "structured_output_object_ok": structured_output_object_ok,
            "structured_output_shape_ok": shape_ok,
            "retrieval_contains_expected_source": checks["retrieval_ok"],
            "source_matches": checks["source_ids_ok"],
            "claim_matches": checks["claim_ok"],
        },
        "answer": answer,
        "error": None,
    }
