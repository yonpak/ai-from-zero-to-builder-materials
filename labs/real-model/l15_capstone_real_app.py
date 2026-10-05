#!/usr/bin/env python3
"""Optional Level 15 extension: run one small real RAG pipeline.

This exercise is intentionally separate from the deterministic Level 15 release
capstone. It demonstrates real embedding retrieval, real model generation,
structured output validation, and deterministic answer rendering.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_GENERATOR = "Qwen/Qwen2.5-0.5B-Instruct"
DEFAULT_OUTPUT = ROOT / "artifacts" / "real-model" / "l15-real-rag-run.json"
DEFAULT_PRODUCT = ROOT / "projects" / "starters" / "l15" / "product.py"
PRODUCT_CHECKER = ROOT / "projects" / "tests" / "l15" / "validate_product.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CLAIM_CONTRACT = load_module(
    Path(__file__).with_name("l15_claim_contract.py"),
    "l15_claim_contract",
)
RUNTIME = load_module(
    Path(__file__).with_name("l15_real_rag_runtime.py"),
    "l15_real_rag_runtime",
)
CORPUS = [dict(row) for row in CLAIM_CONTRACT.CANONICAL_CORPUS]
CASES = [
    {"id": case_id, **spec}
    for case_id, spec in CLAIM_CONTRACT.REAL_RAG_CASE_SPECS.items()
]


def choose_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def preflight_product(product, path: Path, checker) -> None:
    try:
        checker.objective_checks(product)
    except (AssertionError, TypeError, ValueError, KeyError) as error:
        raise SystemExit(f"Level 15 RAG product preflight failed for {path}: {error}") from error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--embedding-revision")
    parser.add_argument("--generator", default=DEFAULT_GENERATOR)
    parser.add_argument("--generator-revision")
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--product",
        type=Path,
        default=DEFAULT_PRODUCT,
        help="completed learner RAG product.py",
    )
    args = parser.parse_args()

    if args.top_k < 1 or args.top_k > len(CORPUS):
        raise SystemExit("--top-k must be between 1 and the corpus size")

    product = load_module(args.product, "l15_learner_product")
    product_checker = load_module(PRODUCT_CHECKER, "l15_product_checker")
    preflight_product(product, args.product, product_checker)

    device = choose_device()
    embedding_kwargs = {"device": device}
    if args.embedding_revision:
        embedding_kwargs["revision"] = args.embedding_revision
    raw_embedder = SentenceTransformer(args.embedding_model, **embedding_kwargs)
    embedder = RUNTIME.TrackedEmbedder(raw_embedder)

    generator_kwargs = {}
    if args.generator_revision:
        generator_kwargs["revision"] = args.generator_revision
    tokenizer = AutoTokenizer.from_pretrained(args.generator, **generator_kwargs)
    dtype = torch.float16 if device in {"cuda", "mps"} else torch.float32
    raw_generator = AutoModelForCausalLM.from_pretrained(
        args.generator,
        dtype=dtype,
        **generator_kwargs,
    )
    raw_generator.to(device)
    raw_generator.eval()
    generator = RUNTIME.TrackedGenerator(raw_generator)

    print(f"product: {args.product}")
    print(f"embedding_model: {args.embedding_model}")
    print(f"generator_model: {args.generator}")
    print(f"device: {device}")

    rows = []
    for case in CASES:
        row = RUNTIME.run_case(
            product=product,
            case=case,
            corpus=CORPUS,
            embedder=embedder,
            tokenizer=tokenizer,
            generator=generator,
            device=device,
            top_k=args.top_k,
            max_new_tokens=args.max_new_tokens,
            claim_contract=CLAIM_CONTRACT,
        )
        rows.append(row)

        print(f"\nQuestion: {case['query']}")
        if row["retrieved"]:
            print("Retrieved:", [item["id"] for item in row["retrieved"]])
        else:
            print("Retrieved: <none>")
        print("Expected claim:", case["expected_claim"])
        print("Model claim:", row["claim"] if row["claim"] is not None else "<not available>")
        print("Real embedder called:", row["checks"]["embedder_called"])
        print("Real generator called:", row["checks"]["generator_called"])
        print("Generation status:", row["checks"]["generation_status"])
        print(
            "Structured output object valid:",
            row["checks"]["structured_output_object_ok"],
        )
        print(
            "Structured output shape valid:",
            row["checks"]["structured_output_shape_ok"],
        )
        print("Claim match:", row["checks"]["claim_matches"])
        print("Source match:", row["checks"]["source_matches"])
        if row["error"] is not None:
            print(
                "Pipeline error:",
                f"{row['error']['stage']}: {row['error']['type']}: {row['error']['message']}",
            )
        print(
            "Rendered answer:",
            row["answer"] if row["answer"] is not None else "<not rendered>",
        )

    mechanics_passed = all(
        row["checks"]["embedder_called"] and row["checks"]["generator_called"]
        for row in rows
    )
    report = {
        "exercise": "l15-real-rag-pipeline",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "device": device,
            "embedding_model": args.embedding_model,
            "embedding_revision": args.embedding_revision or "",
            "generator_model": args.generator,
            "generator_revision": args.generator_revision or "",
        },
        "model_calls": {
            "embedder_encode": embedder.encode_calls,
            "generator_generate": generator.generate_calls,
        },
        "mechanics_passed": mechanics_passed,
        "cases": rows,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nreport: {args.output}")
    print(f"mechanics_passed: {mechanics_passed}")
    print(
        "case_matches:",
        {row["case_id"]: row["checks"]["claim_matches"] for row in rows},
    )
    print(
        "generation_status:",
        {row["case_id"]: row["checks"]["generation_status"] for row in rows},
    )

    if not mechanics_passed:
        raise SystemExit(
            "FAIL: each case must call both the supplied embedding model and generator"
        )

    print("PASS: real retrieval and generation executed; inspect case matches above")


if __name__ == "__main__":
    main()
