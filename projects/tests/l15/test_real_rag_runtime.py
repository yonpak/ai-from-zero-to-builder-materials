#!/usr/bin/env python3
"""Regression tests for the stdlib-only Level 15 real-RAG runtime."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNTIME_PATH = REPO / "labs" / "real-model" / "l15_real_rag_runtime.py"
CONTRACT_PATH = REPO / "labs" / "real-model" / "l15_claim_contract.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = load(RUNTIME_PATH, "l15_real_rag_runtime_test")
contract = load(CONTRACT_PATH, "l15_claim_contract_test")
case = {"id": "warranty-length", **contract.REAL_RAG_CASE_SPECS["warranty-length"]}
corpus = [dict(row) for row in contract.CANONICAL_CORPUS]


class RawEmbedder:
    def encode(self, *args, **kwargs):
        return [[1.0]]


class SuccessfulGenerator:
    def generate(self, *args, **kwargs):
        return [[1]]


class FailingGenerator:
    def generate(self, *args, **kwargs):
        raise RuntimeError("generation failed")


class ProductBase:
    @staticmethod
    def retrieve(embedder, supplied_corpus, query, top_k):
        embedder.encode([query])
        hits = [(supplied_corpus[2], 0.9), (supplied_corpus[0], 0.2)]
        return hits[:top_k]

    @staticmethod
    def build_grounded_messages(query, hits):
        return [{"role": "user", "content": query}]


class ParseFailureProduct(ProductBase):
    @staticmethod
    def generate_grounded_claim(tokenizer, model, device, messages, max_new_tokens):
        model.generate()
        raise ValueError("invalid JSON")


class GeneratorFailureProduct(ProductBase):
    @staticmethod
    def generate_grounded_claim(tokenizer, model, device, messages, max_new_tokens):
        model.generate()
        raise AssertionError("unreachable")


class MalformedShapeProduct(ProductBase):
    @staticmethod
    def generate_grounded_claim(tokenizer, model, device, messages, max_new_tokens):
        model.generate()
        return {"claim": "18 months", "source_ids": "D3"}


class WrongClaimProduct(ProductBase):
    @staticmethod
    def generate_grounded_claim(tokenizer, model, device, messages, max_new_tokens):
        model.generate()
        return {"claim": {"warranty_months": 24}, "source_ids": ["D3"]}


class CorrectClaimProduct(ProductBase):
    @staticmethod
    def generate_grounded_claim(tokenizer, model, device, messages, max_new_tokens):
        model.generate()
        return {"claim": {"warranty_months": 18}, "source_ids": ["D3"]}


def run(product, raw_generator):
    embedder = runtime.TrackedEmbedder(RawEmbedder())
    generator = runtime.TrackedGenerator(raw_generator)
    row = runtime.run_case(
        product=product,
        case=case,
        corpus=corpus,
        embedder=embedder,
        tokenizer=object(),
        generator=generator,
        device="cpu",
        top_k=2,
        max_new_tokens=8,
        claim_contract=contract,
    )
    return row, embedder, generator


row, embedder, generator = run(ParseFailureProduct, SuccessfulGenerator())
if [item["id"] for item in row["retrieved"]] != ["D3", "D1"]:
    raise SystemExit("FAIL: generation parse failure discarded retrieval evidence")
if row["error"] is None or row["error"]["stage"] != "generation":
    raise SystemExit("FAIL: generation parse failure did not record its stage")
if not row["checks"]["embedder_called"] or not row["checks"]["generator_called"]:
    raise SystemExit("FAIL: successful model calls were not recorded before parse failure")
if row["checks"]["generation_status"] != "error":
    raise SystemExit("FAIL: generation parse failure did not report error status")
if row["checks"]["structured_output_object_ok"]:
    raise SystemExit("FAIL: parse failure produced a valid structured object")

row, embedder, generator = run(GeneratorFailureProduct, FailingGenerator())
if [item["id"] for item in row["retrieved"]] != ["D3", "D1"]:
    raise SystemExit("FAIL: generator runtime failure discarded retrieval evidence")
if row["checks"]["generator_called"] or generator.generate_calls != 0:
    raise SystemExit("FAIL: failed underlying generation counted as a successful model call")
if row["checks"]["generation_status"] != "error":
    raise SystemExit("FAIL: generator runtime failure did not report error status")
if row["error"] is None or row["error"]["stage"] != "generation":
    raise SystemExit("FAIL: generator runtime failure stage was not preserved")

row, _, _ = run(MalformedShapeProduct, SuccessfulGenerator())
if row["checks"]["generation_status"] != "returned":
    raise SystemExit("FAIL: returned structured output did not report returned status")
if not row["checks"]["structured_output_object_ok"]:
    raise SystemExit("FAIL: returned dict was not recognized as a structured object")
if row["checks"]["structured_output_shape_ok"]:
    raise SystemExit("FAIL: malformed claim/source field types passed shape validation")
if row["checks"]["claim_matches"] or row["checks"]["source_matches"]:
    raise SystemExit("FAIL: malformed structured output matched the fixed case")
if row["answer"] is not None:
    raise SystemExit("FAIL: malformed structured output rendered an answer")

row, _, _ = run(WrongClaimProduct, SuccessfulGenerator())
if not row["checks"]["embedder_called"] or not row["checks"]["generator_called"]:
    raise SystemExit("FAIL: wrong-claim case did not execute both real-model boundaries")
if not row["checks"]["structured_output_shape_ok"]:
    raise SystemExit("FAIL: well-shaped wrong claim was marked malformed")
if row["checks"]["claim_matches"]:
    raise SystemExit("FAIL: wrong claim unexpectedly matched")
if not row["checks"]["source_matches"]:
    raise SystemExit("FAIL: correct declared source did not match")
if row["answer"] is not None:
    raise SystemExit("FAIL: wrong claim rendered an answer")

row, _, _ = run(CorrectClaimProduct, SuccessfulGenerator())
if row["checks"]["generation_status"] != "returned":
    raise SystemExit("FAIL: successful generation did not report returned status")
if not row["checks"]["structured_output_object_ok"]:
    raise SystemExit("FAIL: successful structured object was not recognized")
if not row["checks"]["structured_output_shape_ok"]:
    raise SystemExit("FAIL: successful structured output failed shape validation")
if not row["checks"]["claim_matches"] or not row["checks"]["source_matches"]:
    raise SystemExit("FAIL: correct claim/source did not match")
if row["answer"] != "The XR-4172 warranty is 18 months. [D3]":
    raise SystemExit("FAIL: correct claim/source did not render the expected answer")

print("PASS: Level 15 real-RAG runtime success and failure-path checks")
