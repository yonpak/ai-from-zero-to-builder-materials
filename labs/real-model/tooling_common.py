"""Shared helpers for optional local real-model tool/agent exercises."""

from __future__ import annotations

import json
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
_TOOL_CALL = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)


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


def generate(tokenizer, model, device: str, messages: list[dict], tools: list | None = None, max_new_tokens: int = 160) -> str:
    kwargs = {
        "add_generation_prompt": True,
        "tokenize": True,
        "return_dict": True,
        "return_tensors": "pt",
    }
    if tools is not None:
        kwargs["tools"] = tools
    batch = tokenizer.apply_chat_template(messages, **kwargs)
    batch = {key: value.to(device) for key, value in batch.items()}
    with torch.inference_mode():
        output_ids = model.generate(
            **batch,
            do_sample=False,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_ids = output_ids[0, batch["input_ids"].shape[1] :]
    return tokenizer.decode(new_ids, skip_special_tokens=True).strip()


def parse_tool_call(text: str) -> dict | None:
    matches = _TOOL_CALL.findall(text)
    if not matches:
        return None
    payload = json.loads(matches[-1])
    name = payload.get("name")
    arguments = payload.get("arguments", {})
    if isinstance(arguments, str):
        arguments = json.loads(arguments)
    if not isinstance(name, str) or not isinstance(arguments, dict):
        raise ValueError("tool call must contain a string name and object arguments")
    return {"name": name, "arguments": arguments}
