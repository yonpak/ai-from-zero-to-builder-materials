"""p09-evidence-rag learner starter.

Complete the TODO functions. The canonical acceptance path is standard-library only.
"""


def token_overlap(query: str, text: str) -> int:
    """Return the count of shared lowercase alphanumeric words."""
    raise NotImplementedError("TODO: normalize both strings and count shared words")


def eligible_source_ids(source_catalog: dict, tenant_id: str) -> list[str]:
    """Return active source IDs authorized for tenant_id, sorted by ID."""
    raise NotImplementedError("TODO: filter by trusted tenant_id and active=True")


def retrieve(query: str, source_catalog: dict, tenant_id: str, k: int = 2) -> list[str]:
    """Rank only eligible sources by token overlap, then source ID for ties."""
    raise NotImplementedError("TODO: filter first, rank second, then return top-k IDs")


def validate_grounded_output(output: dict, supplied_source_ids: list[str]) -> None:
    """Raise ValueError if answer/support/source provenance is inconsistent."""
    raise NotImplementedError("TODO: enforce supported/unsupported output contract")


def validate_run(data: dict) -> None:
    """Raise ValueError when the RAG run violates provenance, ACL, metric, or release rules."""
    raise NotImplementedError("TODO: validate the complete evidence-backed RAG run")
