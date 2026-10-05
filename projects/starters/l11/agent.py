"""p11-bounded-agent learner starter.

Complete the TODO functions. The required validation path uses only the Python standard library and recorded fixtures.
"""


def choose_subgoal(plan: list[dict]) -> str | None:
    """Return the active subgoal, otherwise the first pending subgoal, or None."""
    raise NotImplementedError("TODO: choose active/pending work without reviving completed or blocked subgoals")


def select_action(subgoal: str, available_actions: dict) -> str | None:
    """Choose a permitted action that supports the subgoal, preferring read-only actions."""
    raise NotImplementedError("TODO: filter by supported subgoal and permission, then prefer the narrow read-only action")


def update_working_memory(state: dict, observation: dict, max_recent: int = 3) -> dict:
    """Return updated state using trusted observation fields and a bounded recent-event list."""
    raise NotImplementedError("TODO: preserve explicit control fields, merge trusted fields, and bound recent events")


def memory_write_allowed(candidate: dict, policy: dict) -> bool:
    """Return whether a persistent-memory candidate satisfies category/source/sensitivity/freshness policy."""
    raise NotImplementedError("TODO: enforce memory category, source, sensitive-data, and age rules")


def approval_valid(proposal: dict, approval: dict | None, now_iso: str) -> bool:
    """Return whether approval is granted, unexpired, and bound to the exact action and arguments."""
    raise NotImplementedError("TODO: bind approval to the exact side effect and reject expired/denied records")


def stop_reason(state: dict, max_steps: int, repeat_limit: int) -> str | None:
    """Return a terminal reason such as success, denied, blocked_missing_input, repeated_action, or max_steps."""
    raise NotImplementedError("TODO: apply stop conditions in a deterministic priority order")


def transition(state: str, event: str, transitions: dict) -> str:
    """Return the next state or raise ValueError for an illegal transition."""
    raise NotImplementedError("TODO: apply the explicit STATE|event transition table")


def validate_run(data: dict) -> None:
    """Raise ValueError when a recorded bounded-agent run violates structure, metrics, or release rules."""
    raise NotImplementedError("TODO: validate trajectories and recompute all metrics and the release decision")
