#!/usr/bin/env python3
"""Optional Level 7 extension: run a real instruction-tuned language model locally."""

from __future__ import annotations

import argparse
import json
import random

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


def choose_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(model_id: str):
    device = choose_device()
    dtype = torch.float16 if device in {"cuda", "mps"} else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype)
    model.to(device)
    model.eval()
    return tokenizer, model, device


def generate(tokenizer, model, device: str, messages: list[dict[str, str]]) -> str:
    batch = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    batch = {key: value.to(device) for key, value in batch.items()}
    with torch.inference_mode():
        output_ids = model.generate(
            **batch,
            do_sample=False,
            max_new_tokens=120,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_ids = output_ids[0, batch["input_ids"].shape[1] :]
    return tokenizer.decode(new_ids, skip_special_tokens=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    random.seed(7)
    torch.manual_seed(7)

    incident = "Checkout failed for 11 minutes. Cause is still under investigation."
    vague_messages = [
        {"role": "user", "content": f"Summarize this incident report:\n{incident}"},
    ]
    contract_messages = [
        {
            "role": "system",
            "content": (
                "Return one JSON object with keys impact, cause, and confidence. "
                "Use cause='unknown' when the supplied text does not confirm a cause. "
                "Do not invent facts."
            ),
        },
        {"role": "user", "content": incident},
    ]

    print(f"model_id: {args.model}")
    tokenizer, model, device = load_model(args.model)
    print(f"device: {device}")

    vague = generate(tokenizer, model, device, vague_messages)
    contracted = generate(tokenizer, model, device, contract_messages)

    print("\n=== vague prompt ===")
    print(vague)
    print("\n=== explicit contract ===")
    print(contracted)

    print("\n=== contract check ===")
    try:
        parsed = json.loads(contracted)
    except json.JSONDecodeError as error:
        print(f"structured_output: FAIL ({error})")
    else:
        required = {"impact", "cause", "confidence"}
        missing = sorted(required - parsed.keys())
        print("structured_output:", "PASS" if not missing else f"FAIL missing={missing}")
        print("cause_rule:", "PASS" if parsed.get("cause") == "unknown" else "CHECK MANUALLY")

    print("\nCompare the two outputs. The model is real; the contract checks still belong to application code.")


if __name__ == "__main__":
    main()
