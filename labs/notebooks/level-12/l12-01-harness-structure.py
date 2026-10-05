#!/usr/bin/env python3
from copy import deepcopy

RESTART_AFTER = "policy"


def advance(record, event, external_system):
    row = deepcopy(record)
    if event == "proposal":
        row.update(state="PROPOSED", proposal="get_order")
    elif event == "policy":
        row.update(state="AUTHORIZED", policy="allow")
    elif event == "execute":
        operation_id = row["operation_id"] or "read-order-4172"
        if operation_id not in external_system["applied_operation_ids"]:
            external_system["applied_operation_ids"].add(operation_id)
            external_system["effect_count"] += 1
        row.update(
            state="EXECUTED",
            operation_id=operation_id,
            result="delivered",
        )
    elif event == "complete":
        row.update(state="COMPLETED")
    else:
        raise ValueError(f"unknown event: {event}")
    return row


def next_event(record):
    return {
        "QUEUED": "proposal",
        "PROPOSED": "policy",
        "AUTHORIZED": "execute",
        "EXECUTED": "complete",
    }.get(record["state"])


# This represents the world outside the controller process. It is not controller
# memory, so a controller restart does not reset whether an effect happened.
external_system = {"effect_count": 0, "applied_operation_ids": set()}
record = {"task_id": "T-42", "state": "QUEUED", "operation_id": None}

for event in ["proposal", "policy", "execute", "complete"]:
    record = advance(record, event, external_system)
    if event == RESTART_AFTER:
        break

saved = deepcopy(record)
print("saved:", saved)

# Simulated controller restart: reconstruct controller state only from the durable record.
record = deepcopy(saved)
resume_event = next_event(record)
print("resume from:", resume_event)

while record["state"] != "COMPLETED":
    event = next_event(record)
    if event is None:
        raise RuntimeError(f"cannot resume from state {record['state']}")
    record = advance(record, event, external_system)

print("final:", record)
print("effect_count:", external_system["effect_count"])
assert record["state"] == "COMPLETED"
assert external_system["effect_count"] == 1

# Edge case: the external effect already happened, but durable state still says AUTHORIZED.
# Retrying execute must advance the record without applying the same operation again.
retry_external_system = {
    "effect_count": 1,
    "applied_operation_ids": {"read-order-4172"},
}
retry_record = {
    "task_id": "T-42",
    "state": "AUTHORIZED",
    "operation_id": None,
}
retry_record = advance(retry_record, "execute", retry_external_system)
assert retry_record["state"] == "EXECUTED"
assert retry_record["operation_id"] == "read-order-4172"
assert retry_external_system["effect_count"] == 1

print("PASS: durable state resumes without duplicating the side effect")
