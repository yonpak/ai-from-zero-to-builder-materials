#!/usr/bin/env python3

REPEAT_LIMIT = 3
MAX_STEPS = 5


def stop_reason(snapshot):
    if snapshot.get("success"):
        return "success"
    if snapshot.get("permission_denied"):
        return "denied"
    if snapshot.get("missing_input"):
        return "blocked_missing_input"
    if snapshot.get("repeat_count", 0) >= REPEAT_LIMIT:
        return "repeated_action"
    if snapshot.get("step_count", 0) >= MAX_STEPS:
        return "max_steps"
    return "continue"


cases = {
    "A": {"success": True, "step_count": 2, "repeat_count": 0},
    "B": {"missing_input": True, "step_count": 1, "repeat_count": 0},
    "C": {"repeat_count": 3, "step_count": 3},
    "D": {"repeat_count": 2, "step_count": 3},
    "E": {"repeat_count": 1, "step_count": 4},
    "F": {"repeat_count": 1, "step_count": 5},
    "G": {"permission_denied": True, "step_count": 5, "repeat_count": 3},
}

print(f"REPEAT_LIMIT={REPEAT_LIMIT} MAX_STEPS={MAX_STEPS}")
for name, case in cases.items():
    print(f"{name} => {stop_reason(case)}")
