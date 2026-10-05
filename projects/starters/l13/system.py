from __future__ import annotations

"""Interoperable Agent System learner starter.

Complete the TODO functions, then run the objective validator from the repository root.
"""

MCP_VERSION = "2026-07-28"
A2A_VERSION = "1.0.0"

def protocol_compatible(kind: str, observed_version: str) -> bool:
    # TODO: require the pinned course version for MCP or A2A.
    raise NotImplementedError

def expose_mcp_capabilities(catalog: list[dict], role: str, policy: dict) -> list[str]:
    # TODO: keep only version-compatible capabilities permitted for the local role.
    raise NotImplementedError

def select_agent(cards: list[dict], required_skill: str, required_interface: str) -> str | None:
    # TODO: select a version-compatible A2A agent that advertises both requirements.
    raise NotImplementedError

def artifact_allowed(artifact: dict, expected_task_id: str, expected_types: set[str]) -> bool:
    # TODO: validate task provenance and artifact type.
    raise NotImplementedError

def apply_versioned_update(state: dict, expected_version: int, patch: dict) -> dict:
    # TODO: reject stale writes and increment version on success.
    raise NotImplementedError

def validate_run(data: dict) -> None:
    # TODO: recompute interoperability and coordination metrics from raw events.
    raise NotImplementedError
