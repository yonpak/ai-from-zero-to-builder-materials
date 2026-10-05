from __future__ import annotations

"""Production-Grade Agent Harness learner starter.

Complete the TODO functions, then run:
python3 projects/tests/l12/validate_submission.py projects/starters/l12/harness.py projects/tests/l12/fixtures/passing/harness-run.json
"""

def claim_task(task: dict, worker: str, now_step: int, lease_steps: int) -> dict:
    # TODO: claim unowned or expired work without changing task identity.
    raise NotImplementedError

def operation_key(task_id: str, action: str, arguments: dict) -> str:
    # TODO: return a deterministic identity for the same logical side effect.
    raise NotImplementedError

def retry_decision(error_type: str, attempt: int, max_retries: int) -> dict:
    # TODO: classify retryable failures and return retry + deterministic delay.
    raise NotImplementedError

def authorize(role: str, action: str, policy: dict) -> bool:
    # TODO: recompute permission from role policy and control actions.
    raise NotImplementedError

def sandbox_allows(request: dict, profile: dict) -> bool:
    # TODO: check requested path, host, and memory against the isolation profile.
    raise NotImplementedError

def retrieve_memory(items: list[dict], scope: str, policy: dict, max_items: int) -> list[dict]:
    # TODO: filter by scope, provenance, freshness, then rank and bound.
    raise NotImplementedError

def schedule_waves(dependencies: dict[str, set[str]], max_parallel: int) -> list[list[str]]:
    # TODO: return dependency-respecting waves and reject cycles.
    raise NotImplementedError

def validate_delegation(envelope: dict, parent_tools: set[str], parent_budget: int) -> bool:
    # TODO: ensure child tools, budget, and required evidence stay inside parent bounds.
    raise NotImplementedError

def validate_run(data: dict) -> None:
    # TODO: recompute metrics and release result from raw traces.
    raise NotImplementedError
