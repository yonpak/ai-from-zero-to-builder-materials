"""p08-adapt-small-llm learner starter.

Complete the TODO functions. The canonical acceptance path is standard-library only.
"""


def lora_parameter_count(in_features: int, out_features: int, rank: int) -> int:
    """Return trainable A+B parameter count for one LoRA-adapted matrix."""
    raise NotImplementedError("TODO: rank*in_features + out_features*rank")


def group_split(records: list[dict], validation_groups: set[str]) -> tuple[list[dict], list[dict]]:
    """Split complete group_id values into train or validation."""
    raise NotImplementedError("TODO: keep every group entirely in one split")


def release_decision(
    target_base: float,
    target_adapted: float,
    retention_base: float,
    retention_adapted: float,
    min_target_gain: float,
    max_retention_drop: float,
    critical_regressions: int,
) -> bool:
    """Return whether the adaptation meets all declared release conditions."""
    raise NotImplementedError("TODO: enforce gain, retention-drop, and critical-regression rules")


def validate_run(data: dict) -> None:
    """Raise ValueError when adaptation, structured preference-route, and evaluation evidence is incomplete or inconsistent."""
    raise NotImplementedError("TODO: validate data, adapter lineage, preference route, metrics, release rule, and documentation")
