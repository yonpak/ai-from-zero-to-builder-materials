#!/usr/bin/env python3
"""Lightweight structural checks for the optional Level 15 learner-built RAG product."""

from __future__ import annotations

import ast
import importlib.util
import inspect
import math
import sys
import textwrap
from pathlib import Path


CORPUS = [
    {"id": "D1", "text": "XR-4172 factory reset: hold the rear button for 10 seconds."},
    {"id": "D2", "text": "Warranty coverage for XR-4172 is 18 months from purchase."},
]
QUERY = "How do I factory reset the XR-4172?"


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("l15_product_submission", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot import product module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_hits(hits, top_k: int) -> list[tuple[dict, float]]:
    if not isinstance(hits, list) or len(hits) != top_k:
        raise AssertionError(f"hits must contain exactly {top_k} (document, score) pairs")
    canonical = {row["id"]: row for row in CORPUS}
    normalized = []
    seen_ids: set[str] = set()
    for item in hits:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise AssertionError("each retrieval result must be a (document, score) pair")
        document, score = item
        if not isinstance(document, dict) or document != canonical.get(document.get("id")):
            raise AssertionError("retrieved document must exactly match the supplied corpus row")
        source_id = document["id"]
        if source_id in seen_ids:
            raise AssertionError("retrieved document IDs must be unique")
        if isinstance(score, bool):
            raise AssertionError("retrieval score must be a finite number")
        try:
            numeric_score = float(score)
        except (TypeError, ValueError) as error:
            raise AssertionError("retrieval score must be a finite number") from error
        if not math.isfinite(numeric_score):
            raise AssertionError("retrieval score must be a finite number")
        seen_ids.add(source_id)
        normalized.append((document, numeric_score))
    return normalized


def assert_callable_contract(fn, name: str, args: tuple) -> None:
    try:
        inspect.signature(fn).bind(*args)
    except TypeError as error:
        raise AssertionError(f"{name} signature does not match the starter contract") from error

    try:
        tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    except (OSError, TypeError, SyntaxError):
        return

    function = next(
        (node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))),
        None,
    )
    if function is None:
        return

    for node in ast.walk(function):
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
            if isinstance(node.exc.func, ast.Name) and node.exc.func.id == "NotImplementedError":
                raise AssertionError(f"{name} is still unfinished")
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Name):
            if node.exc.id == "NotImplementedError":
                raise AssertionError(f"{name} is still unfinished")

    body = list(function.body)
    if body and isinstance(body[0], ast.Expr):
        value = body[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            body = body[1:]
    if len(body) == 1:
        statement = body[0]
        if isinstance(statement, ast.Pass):
            raise AssertionError(f"{name} is still unfinished")
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant):
            if statement.value.value is Ellipsis:
                raise AssertionError(f"{name} is still unfinished")
        if isinstance(statement, ast.Return) and (
            statement.value is None
            or (isinstance(statement.value, ast.Constant) and statement.value.value is None)
        ):
            raise AssertionError(f"{name} is still unfinished")


def objective_checks(module) -> None:
    required = (
        "retrieve",
        "build_grounded_messages",
        "generate_grounded_claim",
        "answer_question",
    )
    for name in required:
        if not callable(getattr(module, name, None)):
            raise AssertionError(f"missing callable {name}")

    assert_callable_contract(
        module.retrieve,
        "retrieve",
        (object(), CORPUS, QUERY, 1),
    )
    assert_callable_contract(
        module.build_grounded_messages,
        "build_grounded_messages",
        (QUERY, [(CORPUS[0], 1.0)]),
    )
    assert_callable_contract(
        module.generate_grounded_claim,
        "generate_grounded_claim",
        (object(), object(), "cpu", [{"role": "user", "content": QUERY}], 8),
    )
    assert_callable_contract(
        module.answer_question,
        "answer_question",
        (QUERY, CORPUS, object(), object(), object(), "cpu", 1, 8),
    )

    # Grounded-message construction is pure application logic, so test it directly.
    expected_hits = [(CORPUS[0], 1.0)]
    messages = module.build_grounded_messages(QUERY, expected_hits)
    if not isinstance(messages, list) or not messages:
        raise AssertionError("build_grounded_messages() must return non-empty chat messages")
    if any(not isinstance(row, dict) for row in messages):
        raise AssertionError("each chat message must be a dict")
    flattened = "\n".join(str(row.get("content", "")) for row in messages)
    if QUERY not in flattened or "D1" not in flattened:
        raise AssertionError("grounded messages must include the question and retrieved source ID")
    for field in ("claim", "source_ids"):
        if field not in flattened:
            raise AssertionError(
                "grounded messages must request structured claim and source_ids fields"
            )

    # Test orchestration without pretending to emulate SentenceTransformer or
    # Transformers tensor APIs. The real-model harness tests those APIs after load.
    calls: list[str] = []

    def stub_retrieve(embedder, corpus, query, top_k):
        if corpus != CORPUS or query != QUERY or top_k != 1:
            raise AssertionError("answer_question() changed retrieval inputs")
        calls.append("retrieve")
        return expected_hits

    def stub_build(query, hits):
        if query != QUERY or hits != expected_hits:
            raise AssertionError("answer_question() changed grounding inputs")
        calls.append("build_grounded_messages")
        return messages

    def stub_generate(tokenizer, model, device, built_messages, max_new_tokens):
        if built_messages != messages or device != "cpu" or max_new_tokens != 8:
            raise AssertionError("answer_question() changed generation inputs")
        calls.append("generate_grounded_claim")
        return {
            "claim": {
                "action": "hold",
                "control": "rear_button",
                "seconds": 10,
            },
            "source_ids": ["D1"],
        }

    originals = (
        module.retrieve,
        module.build_grounded_messages,
        module.generate_grounded_claim,
    )
    module.retrieve = stub_retrieve
    module.build_grounded_messages = stub_build
    module.generate_grounded_claim = stub_generate
    try:
        result = module.answer_question(
            QUERY,
            CORPUS,
            object(),
            object(),
            object(),
            "cpu",
            1,
            8,
        )
    finally:
        (
            module.retrieve,
            module.build_grounded_messages,
            module.generate_grounded_claim,
        ) = originals

    if calls != ["retrieve", "build_grounded_messages", "generate_grounded_claim"]:
        raise AssertionError(
            "answer_question() must orchestrate retrieve -> grounded messages -> structured claim generation"
        )
    if not isinstance(result, dict):
        raise AssertionError("answer_question() must return a dict")
    if "answer" in result:
        raise AssertionError(
            "answer_question() must not return free-text answer; verified claims are rendered later"
        )
    claim = result.get("claim")
    if not isinstance(claim, dict):
        raise AssertionError("answer_question() must return a structured claim object")
    if claim != {"action": "hold", "control": "rear_button", "seconds": 10}:
        raise AssertionError("answer_question() changed the generated structured claim")
    source_ids = result.get("source_ids")
    if source_ids != ["D1"]:
        raise AssertionError("answer_question() must preserve generated source_ids")
    final_hits = validate_hits(result.get("hits"), 1)
    if final_hits[0][0]["id"] != "D1":
        raise AssertionError("answer_question() must return the retrieved evidence")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_product.py PRODUCT.py")
    path = Path(sys.argv[1])
    module = load_module(path)
    try:
        objective_checks(module)
    except (AssertionError, TypeError, ValueError, KeyError) as error:
        raise SystemExit("FAIL: Level 15 RAG product contract: " + str(error)) from error
    print("PASS: Level 15 RAG product contract checks")


if __name__ == "__main__":
    main()
