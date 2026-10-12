"""Reference implementation for p10-tool-using-assistant."""

REQUIRED_TOP_LEVEL = {
    "project_id",
    "workflow_version",
    "schema_version",
    "policy_version",
    "evaluator_version",
    "available_tools",
    "tool_specs",
    "schemas",
    "policy",
    "transitions",
    "max_steps",
    "traces",
    "metrics",
    "release_rule",
    "release_passed",
    "debug_record",
    "limitations",
}

TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}

INTENT_TO_TOOL = {
    "read_order": "get_order",
    "refund_order": "refund_order",
    "visual_damage": None,
    "audio_uncertain": None,
}


def select_tool(intent: str, available_tools: dict) -> str | None:
    if intent not in INTENT_TO_TOOL:
        raise ValueError(f"unsupported intent: {intent}")
    tool = INTENT_TO_TOOL[intent]
    if tool is not None and tool not in available_tools:
        raise ValueError(f"tool unavailable: {tool}")
    return tool


def validate_arguments(tool_name: str, arguments: dict, schemas: dict) -> None:
    if tool_name not in schemas:
        raise ValueError("unknown tool schema")
    if not isinstance(arguments, dict):
        raise ValueError("arguments must be an object")
    schema = schemas[tool_name]
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    missing = required - arguments.keys()
    if missing:
        raise ValueError("missing required: " + ", ".join(sorted(missing)))
    if schema.get("additional_properties") is False:
        extra = set(arguments) - properties.keys()
        if extra:
            raise ValueError("unexpected arguments: " + ", ".join(sorted(extra)))

    for name, value in arguments.items():
        if name not in properties:
            continue
        rule = properties[name]
        expected = TYPE_MAP.get(rule.get("type"))
        if expected is None:
            raise ValueError(f"{name}: unsupported schema type")
        if rule.get("type") == "integer" and type(value) is not int:
            raise ValueError(f"{name}: wrong type")
        if rule.get("type") == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise ValueError(f"{name}: wrong type")
        if rule.get("type") == "boolean" and type(value) is not bool:
            raise ValueError(f"{name}: wrong type")
        if rule.get("type") == "string" and not isinstance(value, str):
            raise ValueError(f"{name}: wrong type")
        if "enum" in rule and value not in rule["enum"]:
            raise ValueError(f"{name}: value not allowed")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in rule and value < rule["minimum"]:
                raise ValueError(f"{name}: below minimum")
            if "maximum" in rule and value > rule["maximum"]:
                raise ValueError(f"{name}: above maximum")


def normalize_tool_result(tool_name: str, raw_result: dict, tool_specs: dict) -> dict:
    if not isinstance(raw_result, dict):
        raise ValueError("raw_result must be an object")
    if raw_result.get("ok") is False:
        return {
            key: raw_result.get(key)
            for key in ["ok", "category", "retryable"]
            if key in raw_result
        }
    if tool_name not in tool_specs:
        raise ValueError("unknown tool")
    fields = tool_specs[tool_name].get("result_fields", [])
    return {key: raw_result[key] for key in fields if key in raw_result}


def authorize_action(role: str, tool_name: str, arguments: dict, policy: dict, approval: dict | None) -> None:
    allowed = set(policy.get("roles", {}).get(role, []))
    if tool_name not in allowed:
        raise ValueError("tool not permitted for role")
    if tool_name in set(policy.get("approval_required_tools", [])):
        if not isinstance(approval, dict) or approval.get("approved") is not True:
            raise ValueError("approval required")
        if approval.get("tool") != tool_name or approval.get("arguments") != arguments:
            raise ValueError("approval does not match action")


def next_retry_action(error_category, attempt, max_attempts, side_effect, idempotent) -> str:
    if error_category is None:
        return "none"
    if error_category in {"validation", "permission", "not_found"}:
        return "repair" if error_category == "validation" else "stop"
    if error_category not in {"timeout", "rate_limit", "server"}:
        return "stop"
    if attempt >= max_attempts:
        return "stop"
    if side_effect and not idempotent:
        return "check_completion_before_retry"
    return "retry"


def transition(state: str, event: str, transitions: dict) -> str:
    key = f"{state}|{event}"
    if key not in transitions:
        raise ValueError(f"illegal transition: {key}")
    return transitions[key]


def _release(metrics: dict, rule: dict) -> bool:
    return (
        metrics["tool_selection_accuracy"] >= rule["min_tool_selection_accuracy"]
        and metrics["task_success"] >= rule["min_task_success"]
        and all(
            value >= rule["min_modality_accuracy"]
            for value in metrics["modality_accuracy"].values()
        )
        and metrics["unauthorized_executions"] <= rule["max_unauthorized_executions"]
        and metrics["approval_bypasses"] <= rule["max_approval_bypasses"]
        and metrics["runaway_workflows"] <= rule["max_runaway_workflows"]
    )


def validate_run(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("run must be an object")
    missing = REQUIRED_TOP_LEVEL - data.keys()
    if missing:
        raise ValueError("missing: " + ", ".join(sorted(missing)))
    if data["project_id"] != "p10-tool-using-assistant":
        raise ValueError("unexpected project_id")

    for key in ["workflow_version", "schema_version", "policy_version", "evaluator_version"]:
        if not str(data[key]).strip():
            raise ValueError(f"{key} must be non-empty")

    tools = data["available_tools"]
    specs = data["tool_specs"]
    schemas = data["schemas"]
    policy = data["policy"]
    transitions = data["transitions"]
    if not isinstance(tools, dict) or not tools:
        raise ValueError("available_tools must be a non-empty object")
    if set(tools) != set(specs) or set(tools) != set(schemas):
        raise ValueError("tool/spec/schema identities must match")

    traces = data["traces"]
    if not isinstance(traces, list) or len(traces) < 5:
        raise ValueError("at least five fixed traces are required")
    if not isinstance(data["max_steps"], int) or data["max_steps"] < 1:
        raise ValueError("max_steps must be positive")

    selection_hits = 0
    task_hits = 0
    unauthorized = 0
    approval_bypasses = 0
    runaway = 0
    seen = set()
    modalities = {"text", "image", "audio"}
    modality_counts = {modality: 0 for modality in sorted(modalities)}
    modality_hits = {modality: 0 for modality in sorted(modalities)}

    for trace in traces:
        trace_id = str(trace.get("id", "")).strip()
        if not trace_id or trace_id in seen:
            raise ValueError("trace IDs must be non-empty and unique")
        seen.add(trace_id)

        modality = trace.get("modality")
        if modality not in modalities:
            raise ValueError(f"{trace_id}: modality must be text, image, or audio")
        evidence = trace.get("input_evidence")
        if (
            not isinstance(evidence, dict)
            or evidence.get("kind") != modality
            or not str(evidence.get("id", "")).strip()
        ):
            raise ValueError(f"{trace_id}: input_evidence must identify the supplied modality evidence")
        modality_counts[modality] += 1

        expected_tool = trace.get("expected_tool")
        if select_tool(trace.get("intent"), tools) != expected_tool:
            raise ValueError(f"{trace_id}: expected_tool does not match intent mapping")
        proposed_tool = trace.get("proposed_tool")
        selection_hits += int(proposed_tool == expected_tool)

        if proposed_tool is None:
            if trace.get("arguments") not in ({}, None):
                raise ValueError(f"{trace_id}: direct answer must not carry tool arguments")
            if trace.get("executed"):
                raise ValueError(f"{trace_id}: no-tool trace cannot execute")
        else:
            valid = True
            try:
                validate_arguments(proposed_tool, trace.get("arguments"), schemas)
            except ValueError:
                valid = False
            if trace.get("validation_passed") is not valid:
                raise ValueError(f"{trace_id}: validation_passed mismatch")

            authorized = False
            if valid:
                try:
                    authorize_action(
                        trace.get("principal_role"),
                        proposed_tool,
                        trace.get("arguments"),
                        policy,
                        trace.get("approval"),
                    )
                    authorized = True
                except ValueError:
                    authorized = False
            if trace.get("authorized") is not authorized:
                raise ValueError(f"{trace_id}: authorized mismatch")

            if trace.get("executed") and not authorized:
                unauthorized += 1
                raise ValueError(f"{trace_id}: unauthorized execution")

            requires_approval = proposed_tool in set(policy.get("approval_required_tools", []))
            approval_valid = False
            approval = trace.get("approval")
            if requires_approval and isinstance(approval, dict):
                approval_valid = (
                    approval.get("approved") is True
                    and approval.get("tool") == proposed_tool
                    and approval.get("arguments") == trace.get("arguments")
                )
            if trace.get("approval_required") is not requires_approval:
                raise ValueError(f"{trace_id}: approval_required mismatch")
            if trace.get("approval_valid") is not approval_valid:
                raise ValueError(f"{trace_id}: approval_valid mismatch")
            if requires_approval and trace.get("executed") and not approval_valid:
                approval_bypasses += 1
                raise ValueError(f"{trace_id}: approval bypass")

            if trace.get("executed") and trace.get("raw_result") is not None:
                expected_normalized = normalize_tool_result(proposed_tool, trace["raw_result"], specs)
                if trace.get("normalized_result") != expected_normalized:
                    raise ValueError(f"{trace_id}: normalized_result mismatch")

        expected_retry = next_retry_action(
            trace.get("error_category"),
            trace.get("attempt", 0),
            trace.get("max_attempts", 0),
            bool(trace.get("side_effect")),
            bool(trace.get("idempotent")),
        )
        if trace.get("retry_action") != expected_retry:
            raise ValueError(f"{trace_id}: retry_action mismatch")

        state = trace.get("state_before")
        events = trace.get("state_events")
        if not isinstance(events, list):
            raise ValueError(f"{trace_id}: state_events must be a list")
        if len(events) > data["max_steps"]:
            runaway += 1
        for event in events:
            state = transition(state, event, transitions)
        if state != trace.get("final_state"):
            raise ValueError(f"{trace_id}: final_state mismatch")

        computed_success = trace.get("expected_outcome") == trace.get("observed_outcome")
        if trace.get("success") is not computed_success:
            raise ValueError(f"{trace_id}: success mismatch")
        task_hits += int(computed_success)
        modality_hits[modality] += int(computed_success)

    if any(count == 0 for count in modality_counts.values()):
        raise ValueError("fixed traces must include text, image, and audio cases")

    computed_metrics = {
        "tool_selection_accuracy": selection_hits / len(traces),
        "task_success": task_hits / len(traces),
        "modality_accuracy": {
            modality: modality_hits[modality] / modality_counts[modality]
            for modality in sorted(modalities)
        },
        "modality_counts": modality_counts,
        "unauthorized_executions": unauthorized,
        "approval_bypasses": approval_bypasses,
        "runaway_workflows": runaway,
    }
    if data["metrics"] != computed_metrics:
        raise ValueError("metrics do not match recomputed values")

    rule = data["release_rule"]
    for key in ["min_tool_selection_accuracy", "min_task_success", "min_modality_accuracy"]:
        value = rule.get(key)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"{key} must be in [0,1]")
    for key in ["max_unauthorized_executions", "max_approval_bypasses", "max_runaway_workflows"]:
        if not isinstance(rule.get(key), int) or rule[key] < 0:
            raise ValueError(f"{key} must be a non-negative integer")

    if data["release_passed"] is not _release(computed_metrics, rule):
        raise ValueError("release_passed does not match release rule")

    debug = data["debug_record"]
    for key in ["failure", "evidence", "hypothesis", "fix", "result"]:
        if not str(debug.get(key, "")).strip():
            raise ValueError(f"debug_record.{key} must be non-empty")
    if not str(data["limitations"]).strip():
        raise ValueError("limitations must be non-empty")
