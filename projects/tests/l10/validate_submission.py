#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise AssertionError(message)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("p10_submission", path)
    if spec is None or spec.loader is None:
        fail(f"cannot import submission: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def objective_checks(module, run_data: dict) -> None:
    required = [
        "select_tool",
        "validate_arguments",
        "normalize_tool_result",
        "authorize_action",
        "next_retry_action",
        "transition",
        "validate_run",
    ]
    for name in required:
        if not callable(getattr(module, name, None)):
            fail(f"missing callable {name}")

    tools = {"get_order": {}, "refund_order": {}}
    if module.select_tool("read_order", tools) != "get_order":
        fail("read_order should select get_order")
    if module.select_tool("visual_damage", tools) is not None:
        fail("visual_damage should not require a tool")

    schemas = {
    "get_order": {
        "type": "object",
        "required": [
            "order_id"
        ],
        "additional_properties": False,
        "properties": {
            "order_id": {
                "type": "string"
            }
        }
    },
    "refund_order": {
        "type": "object",
        "required": [
            "order_id",
            "amount"
        ],
        "additional_properties": False,
        "properties": {
            "order_id": {
                "type": "string"
            },
            "amount": {
                "type": "number",
                "minimum": 0.01,
                "maximum": 500
            }
        }
    }
}
    module.validate_arguments("get_order", {"order_id": "4172"}, schemas)
    try:
        module.validate_arguments("refund_order", {"order_id": "4172", "amount": 999}, schemas)
    except ValueError:
        pass
    else:
        fail("amount above maximum must be rejected")
    try:
        module.validate_arguments("refund_order", {"order_id": "4172", "amount": True}, schemas)
    except ValueError:
        pass
    else:
        fail("boolean must not be accepted as a numeric amount")

    specs = {
    "get_order": {
        "result_fields": [
            "order_id",
            "status"
        ]
    },
    "refund_order": {
        "result_fields": [
            "order_id",
            "refund_id",
            "status"
        ]
    }
}
    normalized = module.normalize_tool_result(
        "get_order",
        {"ok": True, "order_id": "4172", "status": "shipped", "secret": "hidden"},
        specs,
    )
    if normalized != {"order_id": "4172", "status": "shipped"}:
        fail("normalization must allowlist result fields")

    policy = {
    "roles": {
        "reader": [
            "get_order"
        ],
        "operator": [
            "get_order",
            "refund_order"
        ]
    },
    "approval_required_tools": [
        "refund_order"
    ]
}
    module.authorize_action("reader", "get_order", {"order_id": "4172"}, policy, None)
    try:
        module.authorize_action(
            "reader",
            "refund_order",
            {"order_id": "4172", "amount": 20},
            policy,
            {"approved": True, "tool": "refund_order", "arguments": {"order_id": "4172", "amount": 20}},
        )
    except ValueError:
        pass
    else:
        fail("reader must not be authorized for refund_order")

    if module.next_retry_action("timeout", 0, 2, False, True) != "retry":
        fail("read timeout should be retryable within budget")
    if module.next_retry_action("timeout", 0, 2, True, False) != "check_completion_before_retry":
        fail("non-idempotent side effect needs completion check")

    transitions = {"START|answer_direct": "DONE"}
    if module.transition("START", "answer_direct", transitions) != "DONE":
        fail("transition should apply explicit transition table")
    try:
        module.transition("DONE", "again", transitions)
    except ValueError:
        pass
    else:
        fail("illegal transition must be rejected")

    module.validate_run(run_data)

    tampered = json.loads(json.dumps(run_data))
    tampered["traces"][3]["input_evidence"]["kind"] = "audio"
    try:
        module.validate_run(tampered)
    except ValueError:
        pass
    else:
        fail("validate_run must reject modality/evidence mismatch")

    tampered = json.loads(json.dumps(run_data))
    tampered["traces"][1]["principal_role"] = "reader"
    tampered["traces"][1]["authorized"] = False
    try:
        module.validate_run(tampered)
    except ValueError:
        pass
    else:
        fail("validate_run must reject unauthorized execution")

    tampered = json.loads(json.dumps(run_data))
    tampered["traces"][1]["approval"]["arguments"]["amount"] = 10
    tampered["traces"][1]["approval_valid"] = False
    try:
        module.validate_run(tampered)
    except ValueError:
        pass
    else:
        fail("validate_run must reject approval argument mismatch")

    tampered = json.loads(json.dumps(run_data))
    tampered["release_passed"] = False
    try:
        module.validate_run(tampered)
    except ValueError:
        pass
    else:
        fail("validate_run must recompute release decision")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_submission.py SUBMISSION.py TOOL-RUN.json")
    module_path = Path(sys.argv[1])
    run_path = Path(sys.argv[2])
    if not module_path.is_file() or not run_path.is_file():
        raise SystemExit("submission module and tool-run.json must exist")
    data = json.loads(run_path.read_text(encoding="utf-8"))
    objective_checks(load_module(module_path), data)
    print("PASS: p10-tool-using-assistant objective checks")


if __name__ == "__main__":
    main()
