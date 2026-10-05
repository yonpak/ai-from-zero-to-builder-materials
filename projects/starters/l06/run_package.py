"""p06-tiny-llm learner starter.

Complete the TODO functions. Keep the reduced validation path standard-library only.
"""

import math


def perplexity(loss: float) -> float:
    """Return exp(loss) for a positive finite average natural-log loss."""
    raise NotImplementedError("TODO: validate loss and return math.exp(loss)")


def repeated_bigram_rate(text: str) -> float:
    """Return the fraction of bigram positions that repeat an earlier bigram."""
    raise NotImplementedError("TODO: compute repeated bigram rate")


def choose_best(records: list[dict]) -> dict:
    """Return the record with the smallest positive finite validation_loss."""
    raise NotImplementedError("TODO: validate records and choose the best checkpoint")


def validate_run(data: dict) -> None:
    """Raise ValueError when required reproducibility/evaluation evidence is invalid."""
    raise NotImplementedError("TODO: validate run package invariants")
