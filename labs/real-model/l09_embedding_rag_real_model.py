#!/usr/bin/env python3
"""Optional Level 9 extension: retrieve with a real embedding model and optionally generate an answer."""

from __future__ import annotations

import argparse

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_GENERATOR = "Qwen/Qwen2.5-0.5B-Instruct"

CORPUS = [
    {"id": "D1", "text": "XR-4172 factory reset: hold the rear button for 10 seconds."},
    {"id": "D2", "text": "The XR-4100 battery normally lasts about eight hours."},
    {"id": "D3", "text": "Warranty coverage for XR-4172 is 18 months from purchase."},
    {"id": "D4", "text": "Resetting a device does not extend or renew its warranty."},
]


def choose_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def retrieve(model: SentenceTransformer, query: str, top_k: int):
    texts = [item["text"] for item in CORPUS]
    document_embeddings = model.encode(texts, normalize_embeddings=True)
    query_embedding = model.encode([query], normalize_embeddings=True)[0]
    scores = np.asarray(document_embeddings) @ np.asarray(query_embedding)
    ranking = np.argsort(-scores)[:top_k]
    return [(CORPUS[index], float(scores[index])) for index in ranking]


def generate_answer(model_id: str, query: str, hits) -> str:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = choose_device()
    dtype = torch.float16 if device in {"cuda", "mps"} else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype)
    model.to(device)
    model.eval()

    evidence = "\n".join(f"[{item['id']}] {item['text']}" for item, _ in hits)
    messages = [
        {
            "role": "system",
            "content": (
                "Answer only from the supplied evidence. Cite source IDs like [D1]. "
                "If the evidence is insufficient, say so."
            ),
        },
        {"role": "user", "content": f"Question: {query}\n\nEvidence:\n{evidence}"},
    ]
    batch = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    batch = {key: value.to(device) for key, value in batch.items()}
    with torch.inference_mode():
        output_ids = model.generate(
            **batch,
            do_sample=False,
            max_new_tokens=80,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_ids = output_ids[0, batch["input_ids"].shape[1] :]
    return tokenizer.decode(new_ids, skip_special_tokens=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--generator", default=DEFAULT_GENERATOR)
    parser.add_argument("--query", default="How long is the XR-4172 warranty?")
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()

    device = choose_device()
    print(f"embedding_model_id: {args.embedding_model}")
    print(f"embedding_device: {device}")
    embedding_model = SentenceTransformer(args.embedding_model, device=device)
    hits = retrieve(embedding_model, args.query, args.top_k)

    print(f"\nquery: {args.query}")
    print("retrieved:")
    for item, score in hits:
        print(f"  {item['id']} score={score:.4f} text={item['text']}")

    if args.generate:
        print(f"\ngenerator_model_id: {args.generator}")
        print("answer:")
        print(generate_answer(args.generator, args.query, hits))
    else:
        print("\nAdd --generate to pass the retrieved evidence to a real instruction-tuned generator.")


if __name__ == "__main__":
    main()
