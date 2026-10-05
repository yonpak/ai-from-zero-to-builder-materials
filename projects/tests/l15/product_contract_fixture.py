"""Deterministic fixture used to self-test the optional Level 15 product checker."""

from __future__ import annotations

import json


def _dot(left, right):
    return sum(float(a) * float(b) for a, b in zip(left, right))


def retrieve(embedder, corpus: list[dict], query: str, top_k: int):
    document_embeddings = embedder.encode(
        [row["text"] for row in corpus],
        normalize_embeddings=True,
    )
    query_embedding = embedder.encode([query], normalize_embeddings=True)[0]
    scored = [
        (row, _dot(vector, query_embedding))
        for row, vector in zip(corpus, document_embeddings)
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [(row, float(score)) for row, score in scored[:top_k]]


def build_grounded_messages(query: str, hits: list[tuple[dict, float]]) -> list[dict]:
    evidence = "\n".join(f"[{row['id']}] {row['text']}" for row, _ in hits)
    return [
        {
            "role": "system",
            "content": (
                "Use only supplied evidence. Return exactly one JSON object with keys "
                "claim and source_ids. Do not return a free-text answer. The claim is "
                "machine-checkable. For the reset procedure use claim fields action, "
                "control, and seconds."
            ),
        },
        {
            "role": "user",
            "content": f"Question: {query}\nEvidence:\n{evidence}",
        },
    ]


def generate_grounded_claim(
    tokenizer,
    model,
    device: str,
    messages: list[dict],
    max_new_tokens: int,
) -> dict:
    batch = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    batch = {key: value.to(device) for key, value in batch.items()}
    output_ids = model.generate(
        **batch,
        do_sample=False,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.eos_token_id,
    )
    new_ids = output_ids[0, batch["input_ids"].shape[1] :]
    text = tokenizer.decode(new_ids, skip_special_tokens=True).strip()
    result = json.loads(text)
    if not isinstance(result, dict):
        raise ValueError("model output must decode to one JSON object")
    return result


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
    hits = retrieve(embedder, corpus, query, top_k)
    messages = build_grounded_messages(query, hits)
    result = generate_grounded_claim(
        tokenizer,
        model,
        device,
        messages,
        max_new_tokens,
    )
    return {**result, "hits": hits}
