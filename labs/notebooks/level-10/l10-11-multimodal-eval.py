#!/usr/bin/env python3

TASK_FAILURE_STAGES = {
    "input_preprocessing",
    "representation_retrieval",
    "perception_transcription",
    "tool_selection",
    "argument_validation",
    "execution",
    "result_normalization",
    "final_reasoning",
}

cases = [
    {
        "id": "t1",
        "modality": "text",
        "task_passed": True,
        "task_failure_stage": None,
        "security_failure": False,
    },
    {
        "id": "t2",
        "modality": "text",
        "task_passed": False,
        "task_failure_stage": "final_reasoning",
        "security_failure": False,
    },
    {
        "id": "i1",
        "modality": "image",
        "task_passed": False,
        "task_failure_stage": "perception_transcription",
        "security_failure": False,
    },
    {
        "id": "i2",
        "modality": "image",
        "task_passed": True,
        "task_failure_stage": None,
        "security_failure": False,
    },
    {
        "id": "a1",
        "modality": "audio",
        "task_passed": False,
        "task_failure_stage": "input_preprocessing",
        "security_failure": False,
    },
    {
        "id": "a2",
        "modality": "audio",
        "task_passed": True,
        "task_failure_stage": None,
        "security_failure": False,
    },
]

vision_observations = {"cracked_screen", "red_warning_icon", "device_on_table"}
vision_claims = [
    ("screen appears cracked", {"cracked_screen"}),
    ("warning icon is visible", {"red_warning_icon"}),
    ("owner dropped device yesterday", {"drop_event_yesterday"}),
]


def claim_status(required_observations):
    return "supported" if required_observations <= vision_observations else "unsupported"


def validate_task_result(row):
    stage = row["task_failure_stage"]

    if row["task_passed"]:
        if stage is not None:
            raise ValueError(
                f"passed case {row['id']} must not have task_failure_stage"
            )
        return

    if stage not in TASK_FAILURE_STAGES:
        raise ValueError(
            f"failed case {row['id']} needs a known task_failure_stage"
        )


def metrics(rows):
    by_modality = {}
    task_failures_by_stage = {}

    for row in rows:
        validate_task_result(row)

        bucket = by_modality.setdefault(row["modality"], [0, 0])
        bucket[1] += 1
        bucket[0] += int(row["task_passed"])

        if not row["task_passed"]:
            stage = row["task_failure_stage"]
            task_failures_by_stage[stage] = task_failures_by_stage.get(stage, 0) + 1

    return {
        "task_success_rate": sum(r["task_passed"] for r in rows) / len(rows),
        "modality_counts": {k: total for k, (_, total) in by_modality.items()},
        "by_modality": {k: passed / total for k, (passed, total) in by_modality.items()},
        "task_failures_by_stage": task_failures_by_stage,
        "security_failures": sum(r["security_failure"] for r in rows),
    }


print("recorded vision evidence")
for text, required in vision_claims:
    print(text, "->", claim_status(required))

report = metrics(cases)
print("\nmultimodal metrics")
print(report)

assert claim_status({"cracked_screen"}) == "supported"
assert claim_status({"drop_event_yesterday"}) == "unsupported"
assert 0.0 <= report["task_success_rate"] <= 1.0
assert set(report["by_modality"]) == {row["modality"] for row in cases}
assert sum(report["modality_counts"].values()) == len(cases)
assert report["modality_counts"] == {
    modality: sum(row["modality"] == modality for row in cases)
    for modality in report["by_modality"]
}
assert sum(report["task_failures_by_stage"].values()) == sum(
    not row["task_passed"] for row in cases
)
assert report["security_failures"] == sum(
    row["security_failure"] for row in cases
)

try:
    metrics([
        {
            "id": "invalid-passed-case",
            "modality": "text",
            "task_passed": True,
            "task_failure_stage": "final_reasoning",
            "security_failure": False,
        }
    ])
except ValueError:
    pass
else:
    raise AssertionError("passed cases with a task failure stage must be rejected")
