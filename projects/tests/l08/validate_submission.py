#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise AssertionError(message)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("p08_submission", path)
    if spec is None or spec.loader is None:
        fail(f"cannot import submission: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def must_reject(module, run_data: dict, message: str) -> None:
    try:
        module.validate_run(run_data)
    except ValueError:
        return
    fail(message)


def objective_checks(module, run_data: dict) -> None:
    for name in [
        "lora_parameter_count",
        "group_split",
        "release_decision",
        "validate_run",
    ]:
        if not callable(getattr(module, name, None)):
            fail(f"missing callable {name}")

    if module.lora_parameter_count(80, 100, 4) != 720:
        fail("LoRA parameter count should be rank*in + out*rank")

    records = [
        {"id": "a1", "group_id": "A"},
        {"id": "a2", "group_id": "A"},
        {"id": "b1", "group_id": "B"},
        {"id": "c1", "group_id": "C"},
    ]
    train, validation = module.group_split(records, {"C"})
    train_groups = {r["group_id"] for r in train}
    validation_groups = {r["group_id"] for r in validation}
    if train_groups & validation_groups:
        fail("group_split leaked a group across splits")
    if validation_groups != {"C"}:
        fail("group_split did not honor validation_groups")

    if not module.release_decision(0.70, 0.80, 0.95, 0.94, 0.08, 0.02, 0):
        fail("release_decision should pass a run that meets all thresholds")
    if module.release_decision(0.70, 0.80, 0.95, 0.80, 0.08, 0.02, 0):
        fail("release_decision must reject excessive retention regression")
    if module.release_decision(0.70, 0.80, 0.95, 0.94, 0.08, 0.02, 1):
        fail("release_decision must reject critical regressions")

    module.validate_run(run_data)

    tampered = json.loads(json.dumps(run_data))
    tampered["adaptation"]["compatible_base_id"] = "different-base"
    must_reject(module, tampered, "validate_run must reject base/adapter lineage mismatch")

    tampered = json.loads(json.dumps(run_data))
    tampered["dataset"]["validation_groups"].append(
        tampered["dataset"]["train_groups"][0]
    )
    must_reject(module, tampered, "validate_run must reject group leakage")

    tampered = json.loads(json.dumps(run_data))
    tampered["release_passed"] = not tampered["release_passed"]
    must_reject(module, tampered, "validate_run must recompute the declared release rule")

    tampered = json.loads(json.dumps(run_data))
    tampered["preference_context"]["independent_evaluation"] = ""
    must_reject(
        module,
        tampered,
        "validate_run must require independent evaluation context for preference/reward claims",
    )

    tampered = json.loads(json.dumps(run_data))
    tampered["preference_context"]["selected_route"] = "same-thing"
    must_reject(
        module,
        tampered,
        "validate_run must distinguish RLHF-style, DPO-style, and unused preference routes",
    )

    tampered = json.loads(json.dumps(run_data))
    tampered["preference_context"]["route_contract"]["dpo_style"] = (
        "reward-model-plus-policy-optimization"
    )
    must_reject(
        module,
        tampered,
        "validate_run must encode RLHF-style and DPO-style as different optimization routes",
    )

    tampered = json.loads(json.dumps(run_data))
    tampered["preference_context"]["independent_evaluation_ids"] = [
        run_data["metrics"]["target"]["id"]
    ]
    must_reject(
        module,
        tampered,
        "validate_run must link independent evaluation to both target and retention metric IDs",
    )

    valid_rlhf = json.loads(json.dumps(run_data))
    valid_rlhf["preference_context"]["selected_route"] = "rlhf-style"
    valid_rlhf["preference_context"]["optimization_route"] = (
        "reward-model-plus-policy-optimization"
    )
    valid_rlhf["preference_context"]["proxy_metric_id"] = "reward-model-score-v1"
    module.validate_run(valid_rlhf)

    tampered = json.loads(json.dumps(valid_rlhf))
    tampered["preference_context"]["proxy_metric_id"] = run_data["metrics"]["target"]["id"]
    must_reject(
        module,
        tampered,
        "validate_run must keep preference/reward proxy metrics separate from independent evaluation IDs",
    )

    valid_dpo = json.loads(json.dumps(run_data))
    valid_dpo["preference_context"]["selected_route"] = "dpo-style"
    valid_dpo["preference_context"]["optimization_route"] = "direct-preference-objective"
    valid_dpo["preference_context"]["proxy_metric_id"] = "dpo-preference-objective-v1"
    module.validate_run(valid_dpo)

    tampered = json.loads(json.dumps(valid_dpo))
    tampered["preference_context"]["optimization_route"] = (
        "reward-model-plus-policy-optimization"
    )
    must_reject(
        module,
        tampered,
        "validate_run must reject a DPO route labeled as RLHF-style policy optimization",
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: validate_submission.py SUBMISSION.py ADAPTATION-RUN.json"
        )
    module_path = Path(sys.argv[1])
    run_path = Path(sys.argv[2])
    if not module_path.is_file() or not run_path.is_file():
        raise SystemExit("submission module and adaptation-run.json must exist")

    data = json.loads(run_path.read_text(encoding="utf-8"))
    objective_checks(load_module(module_path), data)
    print("PASS: p08-adapt-small-llm objective checks")


if __name__ == "__main__":
    main()
