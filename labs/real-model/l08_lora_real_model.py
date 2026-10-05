#!/usr/bin/env python3
"""Optional Level 8 extension: apply and train a real LoRA adapter on a small causal LM."""

from __future__ import annotations

import argparse
import itertools
import random
from pathlib import Path

import torch
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

TRAIN_EXAMPLES = [
    ("Password reset worked after identity verification.", "ALLOW"),
    ("The request is unusual and the account owner is not confirmed.", "REVIEW"),
    ("The message asks for credentials to be copied to an unknown site.", "BLOCK"),
]
EVAL_INPUT = "The requester cannot verify ownership and asks to disable MFA immediately."
SYSTEM = "Classify the request as ALLOW, REVIEW, or BLOCK. Return only the label."


def choose_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_base(model_id: str, device: str):
    dtype = torch.float16 if device in {"cuda", "mps"} else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype)
    model.to(device)
    return tokenizer, model


def generate(tokenizer, model, device: str, user_text: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_text},
    ]
    batch = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    batch = {key: value.to(device) for key, value in batch.items()}
    model.eval()
    with torch.inference_mode():
        output_ids = model.generate(
            **batch,
            do_sample=False,
            max_new_tokens=12,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_ids = output_ids[0, batch["input_ids"].shape[1] :]
    return tokenizer.decode(new_ids, skip_special_tokens=True).strip()


def encode_training_example(tokenizer, user_text: str, target: str, max_length: int):
    prompt_messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_text},
    ]
    full_messages = [*prompt_messages, {"role": "assistant", "content": target}]

    prompt_text = tokenizer.apply_chat_template(
        prompt_messages, add_generation_prompt=True, tokenize=False
    )
    full_text = tokenizer.apply_chat_template(
        full_messages, add_generation_prompt=False, tokenize=False
    )

    prompt_ids = tokenizer(
        prompt_text,
        add_special_tokens=False,
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )["input_ids"]
    batch = tokenizer(
        full_text,
        add_special_tokens=False,
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )
    labels = batch["input_ids"].clone()
    prompt_length = min(prompt_ids.shape[1], labels.shape[1])
    labels[:, :prompt_length] = -100
    batch["labels"] = labels
    return batch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--output", default="artifacts/real-model/l08-lora-adapter")
    args = parser.parse_args()

    random.seed(8)
    torch.manual_seed(8)
    device = choose_device()
    if device == "cpu":
        print("warning: CPU is supported for demonstration but training can be slow; a GPU is recommended.")

    print(f"base_model_id: {args.model}")
    print(f"device: {device}")
    tokenizer, base_model = load_base(args.model, device)
    baseline = generate(tokenizer, base_model, device, EVAL_INPUT)

    config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=4,
        lora_alpha=8,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
        bias="none",
    )
    model = get_peft_model(base_model, config)
    model.config.use_cache = False
    model.print_trainable_parameters()

    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.learning_rate)

    encoded = [
        encode_training_example(tokenizer, text, label, args.max_length)
        for text, label in TRAIN_EXAMPLES
    ]

    model.train()
    for step, example in zip(range(args.steps), itertools.cycle(encoded)):
        batch = {key: value.to(device) for key, value in example.items()}
        optimizer.zero_grad(set_to_none=True)
        loss = model(**batch).loss
        loss.backward()
        optimizer.step()
        print(f"step={step + 1} loss={loss.item():.4f}")

    model.config.use_cache = True
    adapted = generate(tokenizer, model, device, EVAL_INPUT)

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output)

    print("\n=== held-out comparison ===")
    print(f"input: {EVAL_INPUT}")
    print(f"before: {baseline}")
    print(f"after:  {adapted}")
    print(f"adapter_saved_to: {output}")
    print("A few steps are a mechanics demo, not evidence that the adapted model is better.")


if __name__ == "__main__":
    main()
