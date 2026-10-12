"""Reference reduced-path implementation for p08-adapt-small-llm."""


REQUIRED_TOP_LEVEL = {
    "project_id",
    "behavior_gap",
    "base_model_id",
    "dataset",
    "adaptation",
    "adapter_id",
    "metrics",
    "release_passed",
    "model_card",
    "debug_record",
    "preference_context",
}

ROUTE_CONTRACT = {
    "rlhf_style": "reward-model-plus-policy-optimization",
    "dpo_style": "direct-preference-objective",
}

SELECTED_ROUTE_TO_OPTIMIZATION = {
    "not-used": "not-used",
    "rlhf-style": ROUTE_CONTRACT["rlhf_style"],
    "dpo-style": ROUTE_CONTRACT["dpo_style"],
}


def lora_parameter_count(in_features: int, out_features: int, rank: int) -> int:
    if min(in_features, out_features, rank) <= 0:
        raise ValueError("dimensions and rank must be positive")
    return rank * in_features + out_features * rank


def group_split(records: list[dict], validation_groups: set[str]) -> tuple[list[dict], list[dict]]:
    train, validation = [], []
    for row in records:
        group_id = str(row.get("group_id", "")).strip()
        if not group_id:
            raise ValueError("every record needs group_id")
        (validation if group_id in validation_groups else train).append(row)
    return train, validation


def release_decision(
    target_base: float,
    target_adapted: float,
    retention_base: float,
    retention_adapted: float,
    min_target_gain: float,
    max_retention_drop: float,
    critical_regressions: int,
) -> bool:
    target_gain = target_adapted - target_base
    retention_drop = retention_base - retention_adapted
    return (
        target_gain >= min_target_gain
        and retention_drop <= max_retention_drop
        and critical_regressions == 0
    )


def _score(value, name):
    if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


def _validate_preference_context(preference: dict, target_id: str, retention_id: str) -> None:
    if not isinstance(preference, dict):
        raise ValueError("preference_context must be an object")

    if preference.get("route_contract") != ROUTE_CONTRACT:
        raise ValueError(
            "preference_context.route_contract must distinguish RLHF reward-model-plus-policy-optimization "
            "from DPO direct-preference-objective"
        )

    selected_route = preference.get("selected_route")
    if selected_route not in SELECTED_ROUTE_TO_OPTIMIZATION:
        raise ValueError(
            "preference_context.selected_route must be not-used, rlhf-style, or dpo-style"
        )

    expected_optimization = SELECTED_ROUTE_TO_OPTIMIZATION[selected_route]
    if preference.get("optimization_route") != expected_optimization:
        raise ValueError(
            "preference_context.optimization_route does not match selected_route"
        )

    evaluation_ids = preference.get("independent_evaluation_ids")
    if not isinstance(evaluation_ids, list) or not evaluation_ids:
        raise ValueError(
            "preference_context.independent_evaluation_ids must be a non-empty list"
        )
    evaluation_ids = {
        str(value).strip() for value in evaluation_ids if str(value).strip()
    }
    if not {target_id, retention_id}.issubset(evaluation_ids):
        raise ValueError(
            "preference_context.independent_evaluation_ids must include target and retention metric IDs"
        )

    proxy_metric_id = preference.get("proxy_metric_id")
    if selected_route == "not-used":
        if proxy_metric_id not in {None, ""}:
            raise ValueError(
                "preference_context.proxy_metric_id must be empty when no preference route is used"
            )
    else:
        if not str(proxy_metric_id or "").strip():
            raise ValueError(
                "preference_context.proxy_metric_id is required for RLHF-style or DPO-style routes"
            )
        if str(proxy_metric_id).strip() in evaluation_ids:
            raise ValueError(
                "preference proxy metric must remain separate from independent evaluation IDs"
            )

    for key in ["rlhf_vs_dpo", "measured_signal", "independent_evaluation"]:
        if not str(preference.get(key, "")).strip():
            raise ValueError(f"preference_context.{key} must be non-empty")


def validate_run(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("run must be an object")
    missing = REQUIRED_TOP_LEVEL - data.keys()
    if missing:
        raise ValueError("missing: " + ", ".join(sorted(missing)))
    if not str(data["behavior_gap"]).strip():
        raise ValueError("behavior_gap must be non-empty")
    base_id = str(data["base_model_id"]).strip()
    if not base_id:
        raise ValueError("base_model_id must be non-empty")

    ds = data["dataset"]
    for key in ["id", "split_id", "template_version"]:
        if not str(ds.get(key, "")).strip():
            raise ValueError(f"dataset.{key} must be non-empty")
    train_groups = set(ds.get("train_groups", []))
    validation_groups = set(ds.get("validation_groups", []))
    if not train_groups or not validation_groups:
        raise ValueError("train_groups and validation_groups must both be recorded")
    if train_groups & validation_groups:
        raise ValueError("dataset group leakage detected")

    adapt = data["adaptation"]
    if adapt.get("method") not in {"lora", "qlora"}:
        raise ValueError("adaptation.method must be lora or qlora")
    if adapt.get("compatible_base_id") != base_id:
        raise ValueError("adapter/base lineage mismatch")
    rank = adapt.get("rank")
    alpha = adapt.get("alpha")
    if not isinstance(rank, int) or rank <= 0:
        raise ValueError("adaptation.rank must be positive int")
    if not isinstance(alpha, (int, float)) or alpha <= 0:
        raise ValueError("adaptation.alpha must be positive")
    if not isinstance(adapt.get("target_modules"), list) or not adapt["target_modules"]:
        raise ValueError("adaptation.target_modules must be non-empty")
    if not str(data["adapter_id"]).strip():
        raise ValueError("adapter_id must be non-empty")

    metrics = data["metrics"]
    target = metrics.get("target", {})
    retention = metrics.get("retention", {})
    for section_name, section in [("target", target), ("retention", retention)]:
        if not str(section.get("id", "")).strip():
            raise ValueError(f"metrics.{section_name}.id must be non-empty")
        _score(section.get("base"), f"{section_name}.base")
        _score(section.get("adapted"), f"{section_name}.adapted")
    if not isinstance(target.get("min_gain"), (int, float)) or target["min_gain"] < 0:
        raise ValueError("target.min_gain must be non-negative")
    if not isinstance(retention.get("max_drop"), (int, float)) or retention["max_drop"] < 0:
        raise ValueError("retention.max_drop must be non-negative")
    critical = metrics.get("critical_regressions")
    if not isinstance(critical, int) or critical < 0:
        raise ValueError("critical_regressions must be non-negative int")

    _validate_preference_context(
        data["preference_context"],
        str(target["id"]).strip(),
        str(retention["id"]).strip(),
    )

    expected = release_decision(
        target["base"], target["adapted"],
        retention["base"], retention["adapted"],
        target["min_gain"], retention["max_drop"], critical,
    )
    if data["release_passed"] is not expected:
        raise ValueError("release_passed does not match declared metric rule")

    card = data["model_card"]
    if not str(card.get("intended_use", "")).strip():
        raise ValueError("model_card.intended_use must be non-empty")
    limitations = card.get("limitations")
    if not isinstance(limitations, list) or not any(str(x).strip() for x in limitations):
        raise ValueError("model_card.limitations must contain at least one limitation")

    debug = data["debug_record"]
    for key in ["failure", "evidence", "hypothesis", "fix", "result"]:
        if not str(debug.get(key, "")).strip():
            raise ValueError(f"debug_record.{key} must be non-empty")
