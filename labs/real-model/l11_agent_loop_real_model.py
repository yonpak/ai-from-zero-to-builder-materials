#!/usr/bin/env python3
"""Optional Level 11 extension: run a bounded tool-using loop around a real local model."""

from __future__ import annotations

import argparse
import json
import random

import torch

from tooling_common import DEFAULT_MODEL, generate, load_model, parse_tool_call

ORDERS = {"4172": {"order_id": "4172", "status": "shipped", "eta_days": 2}}


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
    parser.add_argument("--max-steps", type=int, default=3)
    args = parser.parse_args()
    if args.max_steps < 1 or args.max_steps > 6:
        raise SystemExit("--max-steps must be between 1 and 6")

    random.seed(11)
    torch.manual_seed(11)
    tokenizer, model, device = load_model(args.model)
    print(f"model_id: {args.model}")
    print(f"device: {device}")
    print(f"max_steps: {args.max_steps}")

    messages = [
        {
            "role": "system",
            "content": (
                "Help with the user's order question. Use get_order_status when status data is needed. "
                "After receiving a tool result, answer the user instead of calling the same tool again."
            ),
        },
        {"role": "user", "content": "What is happening with order 4172, and when should it arrive?"},
    ]
    seen_calls: set[tuple[str, str]] = set()

    for step in range(1, args.max_steps + 1):
        output = generate(tokenizer, model, device, messages, tools=list(TOOLS.values()))
        print(f"\nstep={step} model_output:")
        print(output)

        try:
            call = parse_tool_call(output)
        except (json.JSONDecodeError, ValueError) as error:
            raise SystemExit(f"invalid tool-call structure: {error}") from error

        if call is None:
            print("\nterminal_reason: final_answer")
            return

        name = call["name"]
        arguments = call["arguments"]
        if name not in TOOLS:
            raise SystemExit(f"terminal_reason: blocked_unknown_tool ({name})")
        if set(arguments) != {"order_id"} or not isinstance(arguments["order_id"], str):
            raise SystemExit(f"terminal_reason: blocked_invalid_arguments ({arguments!r})")

        fingerprint = (name, json.dumps(arguments, sort_keys=True))
        if fingerprint in seen_calls:
            raise SystemExit("terminal_reason: repeated_action_blocked")
        seen_calls.add(fingerprint)

        result = TOOLS[name](**arguments)
        print("controller_execution:")
        print(json.dumps(result, indent=2))

        messages.append(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {"name": name, "arguments": arguments},
                    }
                ],
            }
        )
        messages.append({"role": "tool", "name": name, "content": json.dumps(result)})

    raise SystemExit("terminal_reason: step_budget_exhausted")


if __name__ == "__main__":
    main()
