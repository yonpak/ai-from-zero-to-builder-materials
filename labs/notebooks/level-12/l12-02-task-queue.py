#!/usr/bin/env python3


def claim(task, worker, now_step, lease_steps):
    if task.get("owner") and now_step < task["lease_until"]:
        return False
    task["owner"] = worker
    task["lease_until"] = now_step + lease_steps
    task["state"] = "RUNNING"
    return True


task = {"task_id": "T-42", "state": "QUEUED", "owner": None, "lease_until": 0}
lease_steps = 2
original_task_id = task["task_id"]

assert claim(task, "A", 0, lease_steps)
print("step 0: A claimed", task)

for now_step in (1, 2):
    if claim(task, "B", now_step, lease_steps):
        print(f"step {now_step}: B recovered", task)
        break
    print(
        f"step {now_step}: B blocked "
        f"(A's lease runs until step {task['lease_until']})"
    )

assert task["task_id"] == original_task_id
assert task["owner"] == "B"
print("PASS: durable task identity survives lease-based recovery")
