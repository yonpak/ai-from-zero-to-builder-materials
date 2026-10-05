from __future__ import annotations

"""Optional Level 15 learner-built RAG product.

Complete these functions after the required release-evidence controller passes.
The real-model harness supplies the embedding model, tokenizer, generator, device,
corpus, and evaluation cases. This file owns the product path itself.
"""


def retrieve(embedder, corpus: list[dict], query: str, top_k: int):
    """Return the top-k corpus rows as (row, score) pairs."""
    # TODO: embed the corpus and query, rank by similarity, and return top-k rows.
    raise NotImplementedError


def build_grounded_messages(query: str, hits: list[tuple[dict, float]]) -> list[dict]:
    """Build grounded messages that request a machine-checkable result."""
    # TODO: include source IDs and require one JSON object with:
    # {"claim": <structured fact>, "source_ids": [<IDs>]}.
    # The fixed cases use these claim shapes. Derive the values from retrieved evidence:
    # {"warranty_months": <integer>}
    # {"action": <string>, "control": <string>, "seconds": <integer>}
    # {"reset_changes_warranty": <boolean>}
    raise NotImplementedError


def generate_grounded_claim(
    tokenizer,
    model,
    device: str,
    messages: list[dict],
    max_new_tokens: int,
) -> dict:
    """Generate and parse one structured claim with explicit provenance."""
    # TODO: generate only the new assistant tokens, parse the JSON object, and return
    # {"claim": <dict>, "source_ids": <list[str]>}. Do not ask the model for prose.
    raise NotImplementedError


def answer_question(
    query: str,
    corpus: list[dict],
    embedder,
    tokenizer,
    model,
    device: str,
    top_k: int,
    max_new_tokens: int,
) -> dict:
    """Run retrieval -> grounding -> structured claim generation and return evidence."""
    # TODO: orchestrate the three product steps above.
    # Return {
    #   "claim": <dict>,
    #   "source_ids": <list[str]>,
    #   "hits": [(document, score), ...],
    # }.
    raise NotImplementedError
