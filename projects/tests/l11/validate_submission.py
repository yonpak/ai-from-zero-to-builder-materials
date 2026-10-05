#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise AssertionError(message)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("p11_submission", path)
    if spec is None or spec.loader is None:
        fail(f"cannot import submission: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expect_value_error(call, message: str) -> None:
    try:
        call()
    except ValueError:
        return
    fail(message)


def objective_checks(module, run_data: dict) -> None:
    required = [
        "choose_subgoal",
        "select_action",
        "update_working_memory",
        "memory_write_allowed",
        "approval_valid",
        "stop_reason",
        "transition",
        "validate_run",
    ]
    for name in required:
        if not callable(getattr(module, name, None)):
            fail(f"missing callable {name}")

    plan = [
        {"name": "done", "status": "completed"},
        {"name": "current", "status": "active"},
        {"name": "later", "status": "pending"},
    ]
    if module.choose_subgoal(plan) != "current":
        fail("choose_subgoal should prefer the active subgoal")
    if module.choose_subgoal([
        {"name": "done", "status": "completed"},
        {"name": "later", "status": "pending"},
    ]) != "later":
        fail("choose_subgoal should select the first pending subgoal when none is active")
    if module.choose_subgoal([{"name": "done", "status": "completed"}]) is not None:
        fail("choose_subgoal should return None when no work remains")
    expect_value_error(
        lambda: module.choose_subgoal([
            {"name": "a", "status": "active"},
            {"name": "b", "status": "active"},
        ]),
        "multiple active subgoals must be rejected",
    )

    actions = {
        "broad_write": {
            "permitted": True,
            "supports_subgoals": ["learn_status"],
            "side_effect": True,
            "priority": 1,
        },
        "narrow_read": {
            "permitted": True,
            "supports_subgoals": ["learn_status"],
            "side_effect": False,
            "priority": 5,
        },
        "denied_read": {
            "permitted": False,
            "supports_subgoals": ["learn_status"],
            "side_effect": False,
            "priority": 0,
        },
    }
    if module.select_action("learn_status", actions) != "narrow_read":
        fail("select_action should filter denied actions and prefer a permitted read-only action")
    if module.select_action("unknown", actions) is not None:
        fail("select_action should return None when no action supports the subgoal")

    state = {
        "step_count": 2,
        "approval_status": "pending",
        "recent": [{"source": "old"}],
        "order_status": "shipping",
    }
    observation = {
        "source": "order_tool",
        "trusted": True,
        "fields": {
            "order_status": "delivered",
            "step_count": 999,
            "approval_status": "approved",
        },
    }
    updated = module.update_working_memory(state, observation, max_recent=2)
    if updated.get("order_status") != "delivered":
        fail("trusted observation should update ordinary working-state fields")
    if updated.get("order_status_source") != "order_tool":
        fail("working-memory update should preserve field provenance")
    if updated.get("step_count") != 2 or updated.get("approval_status") != "pending":
        fail("observation data must not overwrite controller-owned state fields")
    if len(updated.get("recent", [])) > 2:
        fail("recent-event working memory must respect max_recent")

    untrusted = module.update_working_memory(
        {"value": "trusted", "recent": []},
        {"source": "model", "trusted": False, "fields": {"value": "guess"}},
        max_recent=1,
    )
    if untrusted.get("value") != "trusted":
        fail("untrusted observation must not overwrite trusted working state")

    memory_policy = {
        "allowed_categories": ["preference", "task_summary"],
        "trusted_sources": ["profile", "verified_tool"],
        "allow_sensitive": False,
        "max_age_days": 30,
    }
    good_memory = {
        "category": "preference",
        "source": "profile",
        "sensitive": False,
        "age_days": 2,
    }
    if not module.memory_write_allowed(good_memory, memory_policy):
        fail("valid scoped memory candidate should be allowed")
    if module.memory_write_allowed({**good_memory, "source": "model_guess"}, memory_policy):
        fail("untrusted memory provenance must be rejected")
    if module.memory_write_allowed({**good_memory, "sensitive": True}, memory_policy):
        fail("sensitive memory must be rejected when policy forbids it")
    if module.memory_write_allowed({**good_memory, "age_days": 120}, memory_policy):
        fail("stale memory candidate must be rejected")

    proposal = {
        "action": "refund_order",
        "arguments": {"order_id": "4172", "amount": 20},
    }
    approval = {
        "approved": True,
        "action": "refund_order",
        "arguments": {"order_id": "4172", "amount": 20},
        "expires_at": "2026-09-23T19:00:00Z",
    }
    if not module.approval_valid(proposal, approval, "2026-09-23T18:00:00Z"):
        fail("exact unexpired approval should validate")
    if module.approval_valid(
        proposal,
        {**approval, "arguments": {"order_id": "4172", "amount": 10}},
        "2026-09-23T18:00:00Z",
    ):
        fail("approval with mismatched arguments must be rejected")
    if module.approval_valid(proposal, approval, "2026-09-23T20:00:00Z"):
        fail("expired approval must be rejected")

    if module.stop_reason({"success": True, "step_count": 1}, 4, 3) != "success":
        fail("successful run should stop as success")
    if module.stop_reason({"permission_denied": True, "step_count": 1}, 4, 3) != "denied":
        fail("permission denial should produce denied stop reason")
    if module.stop_reason({"repeat_count": 3, "step_count": 3}, 4, 3) != "repeated_action":
        fail("repeat limit should stop repeated actions")
    if module.stop_reason({"step_count": 4}, 4, 3) != "max_steps":
        fail("maximum step limit should stop the run")

    transitions = {
        "START|observe": "ACTIVE",
        "ACTIVE|done": "DONE",
    }
    if module.transition("START", "observe", transitions) != "ACTIVE":
        fail("transition should use the explicit transition table")
    expect_value_error(
        lambda: module.transition("DONE", "observe", transitions),
        "illegal transition must be rejected",
    )

    module.validate_run(run_data)

    tampered = json.loads(json.dumps(run_data))
    tampered["traces"][1]["principal_role"] = "reader"
    expect_value_error(
        lambda: module.validate_run(tampered),
        "validate_run must reject an unauthorized executed side effect",
    )

    tampered = json.loads(json.dumps(run_data))
    tampered["traces"][1]["steps"][3]["approval"]["arguments"]["amount"] = 10
    expect_value_error(
        lambda: module.validate_run(tampered),
        "validate_run must reject exact-approval mismatch",
    )

    tampered = json.loads(json.dumps(run_data))
    tampered["traces"][0]["steps"][0]["subgoal"] = "unrelated_goal"
    expect_value_error(
        lambda: module.validate_run(tampered),
        "validate_run must detect goal drift outside allowed subgoals",
    )

    tampered = json.loads(json.dumps(run_data))
    tampered["traces"][4]["memory_writes"].append({
        "candidate": {
            "category": "account_secret",
            "source": "model_guess",
            "sensitive": True,
            "age_days": 1,
        },
        "executed": True,
    })
    expect_value_error(
        lambda: module.validate_run(tampered),
        "validate_run must reject a prohibited executed memory write",
    )

    tampered = json.loads(json.dumps(run_data))
    repeat_trace = tampered["traces"][3]
    extra = json.loads(json.dumps(repeat_trace["steps"][-1]))
    extra["index"] = 4
    repeat_trace["steps"].append(extra)
    expect_value_error(
        lambda: module.validate_run(tampered),
        "validate_run must reject continued execution after the repeated-action limit",
    )

    tampered = json.loads(json.dumps(run_data))
    tampered["release_passed"] = False
    expect_value_error(
        lambda: module.validate_run(tampered),
        "validate_run must recompute release_passed instead of trusting the submitted flag",
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_submission.py SUBMISSION.py AGENT-RUN.json")
    module_path = Path(sys.argv[1])
    run_path = Path(sys.argv[2])
    if not module_path.is_file() or not run_path.is_file():
        raise SystemExit("submission module and agent-run.json must exist")
    data = json.loads(run_path.read_text(encoding="utf-8"))
    objective_checks(load_module(module_path), data)
    print("PASS: p11-bounded-agent objective checks")


if __name__ == "__main__":
    main()
