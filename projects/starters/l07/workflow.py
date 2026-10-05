"""p07-reliable-llm-workflow learner starter.

Complete the TODO functions. Keep the reduced validation path standard-library only.
"""


def word_overlap(query: str, text: str) -> int:
    """Return the number of shared lowercase whitespace-delimited words."""
    raise NotImplementedError("TODO: normalize query/text and count shared words")


def retrieve(query: str, documents: dict[str, str], k: int = 1) -> list[str]:
    """Return up to k document IDs ranked by word overlap, then ID for tie-breaking."""
    raise NotImplementedError("TODO: rank supplied documents without inventing new IDs")


def validate_model_output(output: dict, supplied_source_ids: list[str]) -> None:
    """Raise ValueError when the structured output violates grounding/provenance rules."""
    raise NotImplementedError("TODO: validate answer/supported/source_id invariants")


def evaluate_cases(cases: list[dict]) -> tuple[int, list[str]]:
    """Return (passed_count, failing_case_ids) using each case's expected answer/support state."""
    raise NotImplementedError("TODO: evaluate fixed cases and preserve failing IDs")


def validate_run(data: dict) -> None:
    """Raise ValueError when the workflow run package is incomplete or inconsistent."""
    raise NotImplementedError("TODO: validate reproducibility, cases, provenance, and debug evidence")
