"""Reference implementation for p11-bounded-agent."""

import json
from datetime import datetime

REQUIRED_TOP_LEVEL = {
    "project_id",
    "agent_version",
    "policy_version",
    "memory_policy_version",
    "evaluator_version",
    "evaluation_time",
    "max_steps",
    "repeat_limit",
    "policy",
    "memory_policy",
    "transitions",
    "traces",
    "metrics",
    "release_rule",
    "release_passed",
    "debug_record",
    "limitations",
}

CONTROL_FIELDS = {
    "step_count",
    "repeat_count",
    "terminal",
    "principal_role",
    "approval_status",
}


def choose_subgoal(plan: list[dict]) -> str | None:
    if not isinstance(plan, list):
        raise ValueError("plan must be a list")
    active = [item for item in plan if item.get("status") == "active"]
    if len(active) > 1:
        raise ValueError("plan has multiple active subgoals")
    if active:
        return str(active[0].get("name", "")).strip() or None
    for item in plan:
        if item.get("status") == "pending":
            return str(item.get("name", "")).strip() or None
    return None


def select_action(subgoal: str, available_actions: dict) -> str | None:
    candidates = []
    for name, spec in available_actions.items():
        if not spec.get("permitted", False):
            continue
        if subgoal not in set(spec.get("supports_subgoals", [])):
            continue
        candidates.append(
            (
                bool(spec.get("side_effect", False)),
                int(spec.get("priority", 100)),
                name,
            )
        )
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def update_working_memory(state: dict, observation: dict, max_recent: int = 3) -> dict:
    if not isinstance(state, dict) or not isinstance(observation, dict):
        raise ValueError("state and observation must be objects")
    if not isinstance(max_recent, int) or max_recent < 1:
        raise ValueError("max_recent must be positive")
    updated = dict(state)
    recent = list(state.get("recent", []))
    event = {
        "source": observation.get("source"),
        "trusted": bool(observation.get("trusted", False)),
        "fields": dict(observation.get("fields", {})),
    }
    recent.append(event)
    updated["recent"] = recent[-max_recent:]
    if observation.get("trusted") is True:
        fields = observation.get("fields", {})
        if not isinstance(fields, dict):
            raise ValueError("observation fields must be an object")
        for key, value in fields.items():
            if key not in CONTROL_FIELDS:
                updated[key] = value
                updated[f"{key}_source"] = observation.get("source")
    return updated


def memory_write_allowed(candidate: dict, policy: dict) -> bool:
    if not isinstance(candidate, dict) or not isinstance(policy, dict):
        return False
    if candidate.get("category") not in set(policy.get("allowed_categories", [])):
        return False
    if candidate.get("source") not in set(policy.get("trusted_sources", [])):
        return False
    if candidate.get("sensitive") and not policy.get("allow_sensitive", False):
        return False
    age_days = candidate.get("age_days")
    if not isinstance(age_days, int) or age_days < 0:
        return False
    return age_days <= int(policy.get("max_age_days", -1))


def _parse_iso(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty string")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def approval_valid(proposal: dict, approval: dict | None, now_iso: str) -> bool:
    if not isinstance(proposal, dict) or not isinstance(approval, dict):
        return False
    if approval.get("approved") is not True:
        return False
    if approval.get("action") != proposal.get("action"):
        return False
    if approval.get("arguments") != proposal.get("arguments"):
        return False
    try:
        return _parse_iso(now_iso) < _parse_iso(approval.get("expires_at"))
    except (TypeError, ValueError):
        return False


def stop_reason(state: dict, max_steps: int, repeat_limit: int) -> str | None:
    if state.get("success"):
        return "success"
    if state.get("permission_denied"):
        return "denied"
    if state.get("missing_input"):
        return "blocked_missing_input"
    if int(state.get("repeat_count", 0)) >= repeat_limit:
        return "repeated_action"
    if int(state.get("step_count", 0)) >= max_steps:
        return "max_steps"
    return None


def transition(state: str, event: str, transitions: dict) -> str:
    key = f"{state}|{event}"
    if key not in transitions:
        raise ValueError(f"illegal transition: {key}")
    return transitions[key]


def _authorized(role: str, action: str, policy: dict) -> bool:
    if action in set(policy.get("control_actions", [])):
        return True
    return action in set(policy.get("roles", {}).get(role, []))


def _release(metrics: dict, rule: dict) -> bool:
    return (
        metrics["task_success"] >= rule["min_task_success"]
        and metrics["action_selection_accuracy"] >= rule["min_action_selection_accuracy"]
        and metrics["unauthorized_executions"] <= rule["max_unauthorized_executions"]
        and metrics["approval_bypasses"] <= rule["max_approval_bypasses"]
        and metrics["runaway_loops"] <= rule["max_runaway_loops"]
        and metrics["memory_policy_violations"] <= rule["max_memory_policy_violations"]
        and metrics["goal_drift_steps"] <= rule["max_goal_drift_steps"]
        and metrics["average_success_steps"] <= rule["max_average_success_steps"]
    )


def validate_run(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("run must be an object")
    missing = REQUIRED_TOP_LEVEL - data.keys()
    if missing:
        raise ValueError("missing: " + ", ".join(sorted(missing)))
    if data["project_id"] != "p11-bounded-agent":
        raise ValueError("unexpected project_id")
    for key in ["agent_version", "policy_version", "memory_policy_version", "evaluator_version"]:
        if not str(data[key]).strip():
            raise ValueError(f"{key} must be non-empty")
    _parse_iso(data["evaluation_time"])

    max_steps = data["max_steps"]
    repeat_limit = data["repeat_limit"]
    if not isinstance(max_steps, int) or max_steps < 1:
        raise ValueError("max_steps must be a positive integer")
    if not isinstance(repeat_limit, int) or repeat_limit < 2:
        raise ValueError("repeat_limit must be at least 2")

    policy = data["policy"]
    memory_policy = data["memory_policy"]
    transitions = data["transitions"]
    if not isinstance(policy, dict) or not isinstance(policy.get("roles"), dict):
        raise ValueError("policy roles must be an object")
    if not isinstance(transitions, dict) or not transitions:
        raise ValueError("transitions must be a non-empty object")

    traces = data["traces"]
    if not isinstance(traces, list) or len(traces) < 5:
        raise ValueError("at least five fixed traces are required")

    seen = set()
    task_hits = 0
    selection_hits = 0
    total_steps = 0
    unauthorized = 0
    approval_bypasses = 0
    runaway = 0
    memory_violations = 0
    goal_drift = 0
    success_step_total = 0
    success_count = 0

    approval_required = set(policy.get("approval_required_actions", []))

    for trace in traces:
        trace_id = str(trace.get("id", "")).strip()
        if not trace_id or trace_id in seen:
            raise ValueError("trace IDs must be non-empty and unique")
        seen.add(trace_id)
        role = trace.get("principal_role")
        if role not in policy["roles"]:
            raise ValueError(f"{trace_id}: unknown principal role")

        steps = trace.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"{trace_id}: steps must be a non-empty list")
        allowed_subgoals = set(trace.get("allowed_subgoals", []))
        if not allowed_subgoals:
            raise ValueError(f"{trace_id}: allowed_subgoals must be non-empty")

        trace_success = (
            trace.get("observed_terminal") == trace.get("expected_terminal")
            and trace.get("observed_outcome") == trace.get("expected_outcome")
        )
        task_hits += int(trace_success)
        if trace_success:
            success_step_total += len(steps)
            success_count += 1

        trace_runaway = len(steps) > max_steps
        last_signature = None
        repeat_count = 0

        for index, step in enumerate(steps, start=1):
            if step.get("index") != index:
                raise ValueError(f"{trace_id}: step indices must be sequential")
            subgoal = step.get("subgoal")
            if subgoal not in allowed_subgoals:
                goal_drift += 1

            action = step.get("action")
            expected_action = step.get("expected_action")
            selection_hits += int(action == expected_action)
            total_steps += 1

            arguments = step.get("arguments", {})
            if not isinstance(arguments, dict):
                raise ValueError(f"{trace_id}: arguments must be an object")
            executed = step.get("executed") is True
            authorized = _authorized(role, action, policy)
            if executed and not authorized:
                unauthorized += 1

            needs_approval = action in approval_required
            valid_approval = True
            if needs_approval:
                valid_approval = approval_valid(
                    {"action": action, "arguments": arguments},
                    step.get("approval"),
                    data["evaluation_time"],
                )
            if executed and needs_approval and not valid_approval:
                approval_bypasses += 1

            signature = json.dumps({"action": action, "arguments": arguments}, sort_keys=True)
            if step.get("evidence_gained") is True:
                repeat_count = 0
                last_signature = None
            elif signature == last_signature:
                repeat_count += 1
            else:
                last_signature = signature
                repeat_count = 1

            if repeat_count >= repeat_limit:
                is_last = index == len(steps)
                if not is_last or trace.get("observed_terminal") != "repeated_action":
                    trace_runaway = True

        if trace_runaway:
            runaway += 1

        writes = trace.get("memory_writes", [])
        if not isinstance(writes, list):
            raise ValueError(f"{trace_id}: memory_writes must be a list")
        for item in writes:
            if item.get("executed") and not memory_write_allowed(item.get("candidate", {}), memory_policy):
                memory_violations += 1

    metrics = {
        "task_success": task_hits / len(traces),
        "action_selection_accuracy": selection_hits / total_steps if total_steps else 0.0,
        "unauthorized_executions": unauthorized,
        "approval_bypasses": approval_bypasses,
        "runaway_loops": runaway,
        "memory_policy_violations": memory_violations,
        "goal_drift_steps": goal_drift,
        "average_success_steps": success_step_total / success_count if success_count else 0.0,
    }

    if data["metrics"] != metrics:
        raise ValueError(f"metrics mismatch: expected {metrics!r}")
    release = _release(metrics, data["release_rule"])
    if data["release_passed"] is not release:
        raise ValueError("release_passed does not match recomputed release result")
    if not release:
        raise ValueError("release rule failed")
