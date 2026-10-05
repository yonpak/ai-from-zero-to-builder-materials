#!/usr/bin/env python3
"""Validate a training record and model card as one reproducible package."""

from __future__ import annotations

import argparse

TRAINING_RECORD = {
    "base_model_id": "tiny-base-2026-08",
    "parent_artifact_id": "tiny-base-2026-08",
    "dataset_id": "support-format-v3",
    "split_id": "grouped-by-case-v1",
    "template_version": "chat-template-v2",
    "method": "LoRA",
    "adapter_config": {"rank": 8, "alpha": 16, "target_modules": ["q_proj", "v_proj"]},
    "seed": 17,
    "output_adapter_id": "adapter-support-v2",
    "target_eval_id": "support-format-v3-heldout",
    "retention_eval_id": "retention-general-v2",
}

MODEL_CARD = {
    "adapter_id": "adapter-support-v2",
    "base_model_id": "tiny-base-2026-08",
    "intended_use": "Format English support replies into the diagnostic-label schema.",
    "results": {
        "support-format-v3-heldout": "91/100 (base 78/100)",
        "retention-general-v2": "94/100 (base 95/100)",
    },
    "limitations": [
        "Not evaluated on Korean input or contexts above 4k tokens.",
    ],
}

REQUIRED = (
    "base_model_id",
    "parent_artifact_id",
    "dataset_id",
    "split_id",
    "template_version",
    "method",
    "adapter_config",
    "output_adapter_id",
    "target_eval_id",
    "retention_eval_id",
)

VAGUE_LIMITATIONS = {
    "the model may make mistakes.",
    "use with caution.",
    "the model might be imperfect.",
}


def validate(record: dict, card: dict) -> list[str]:
    problems = []
    for field in REQUIRED:
        if not record.get(field):
            problems.append(f"training record missing {field}")

    if record.get("output_adapter_id") != card.get("adapter_id"):
        problems.append("model card adapter_id does not match output_adapter_id")
    if record.get("base_model_id") != card.get("base_model_id"):
        problems.append("model card base_model_id does not match training record")

    results = card.get("results", {})
    for field in ("target_eval_id", "retention_eval_id"):
        eval_id = record.get(field)
        if eval_id and eval_id not in results:
            problems.append(f"model card has no result for {eval_id}")

    limitations = card.get("limitations", [])
    if not limitations:
        problems.append("model card must list at least one limitation")
    for limitation in limitations:
        if limitation.strip().lower() in VAGUE_LIMITATIONS:
            problems.append(f"limitation is too vague: {limitation}")

    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drop", choices=REQUIRED, help="simulate one missing training-record field")
    parser.add_argument("--vague-limitation", action="store_true")
    args = parser.parse_args()

    record = dict(TRAINING_RECORD)
    card = dict(MODEL_CARD)
    card["results"] = dict(MODEL_CARD["results"])
    card["limitations"] = list(MODEL_CARD["limitations"])

    if args.drop:
        record.pop(args.drop, None)
        print(f"(simulation) removed field: {args.drop}")
    if args.vague_limitation:
        card["limitations"] = ["The model may make mistakes."]

    problems = validate(record, card)
    print("adapter:", record.get("output_adapter_id"))
    print("base:", record.get("base_model_id"))
    print("evaluations:", record.get("target_eval_id"), record.get("retention_eval_id"))

    if problems:
        for problem in problems:
            print("FAIL:", problem)
        raise SystemExit(1)

    print("PASS: training record and model card agree on lineage, evaluations, and limitations")


if __name__ == "__main__":
    main()
