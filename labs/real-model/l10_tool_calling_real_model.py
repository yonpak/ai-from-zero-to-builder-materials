#!/usr/bin/env python3
"""Optional Level 10 extension: let a real local model propose a tool call, then validate it in application code."""

from __future__ import annotations

import argparse
import json
import random

import torch

from tooling_common import DEFAULT_MODEL, generate, load_model, parse_tool_call

ORDERS = {
    "4172": {"order_id": "4172", "status": "shipped", "eta_days": 2},
    "9001": {"order_id": "9001", "status": "processing", "eta_days": 5},
}


def get_order_status(order_id: str) -> dict:
    """Look up a demo order.

    Args:
        order_id: The order identifier to retrieve.
    """
    return ORDERS.get(order_id, {"order_id": order_id, "status": "not_found"})


TOOLS = {"get_order_status": get_order_status}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--request", default="Check the status of order 4172. Use the available tool instead of guessing.")
    args = parser.parse_args()

    random.seed(10)
    torch.manual_seed(10)
    tokenizer, model, device = load_model(args.model)
    print(f"model_id: {args.model}")
    print(f"device: {device}")

    messages = [
        {
            "role": "system",
            "content": "Use an available tool when the request needs external order data. Never invent an order status.",
        },
        {"role": "user", "content": args.request},
    ]
    raw = generate(tokenizer, model, device, messages, tools=list(TOOLS.values()))
    print("\nmodel_proposal:")
    print(raw)

    try:
        call = parse_tool_call(raw)
    except (json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"invalid tool-call structure: {error}") from error
    if call is None:
        raise SystemExit("model did not produce a tool call; inspect the proposal above")

    name = call["name"]
    arguments = call["arguments"]
    if name not in TOOLS:
        raise SystemExit(f"blocked undeclared tool: {name}")
    if set(arguments) != {"order_id"} or not isinstance(arguments["order_id"], str):
        raise SystemExit(f"blocked invalid arguments: {arguments!r}")

    result = TOOLS[name](**arguments)
    print("\nvalidated_execution:")
    print(json.dumps({"tool": name, "arguments": arguments, "result": result}, indent=2))
    print("\nThe model proposed the call; application code still owned authorization, schema checks, and execution.")


if __name__ == "__main__":
    main()
