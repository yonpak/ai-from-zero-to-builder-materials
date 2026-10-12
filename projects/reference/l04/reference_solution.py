"""Reference implementation for p04-tokenizer-workbench."""

from __future__ import annotations

import re

SPECIAL_TOKENS = ["<pad>", "<unk>", "<bos>", "<eos>"]
TRAIN_TEXT = [
    "tiny models learn",
    "models predict tokens",
    "play players played",
]
EVAL_CASES = {
    "familiar": "tiny models predict",
    "rare_name": "quokka predicts",
    "emoji": "tiny 🙂",
    "multilingual": "모델 learns",
}
EMBEDDING_TABLE = [
    [0.0, 0.0, 0.0],
    [0.1, 0.1, 0.1],
    [0.2, -0.1, 0.3],
    [-0.2, 0.4, 0.1],
] + [[round(i / 10, 2), round((i % 3) / 10, 2), round(-(i % 5) / 10, 2)] for i in range(4, 32)]


def word_tokens(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", text.lower(), flags=re.UNICODE)


def _split_suffix(piece: str) -> list[str]:
    if not piece.isalpha():
        return [piece]
    for suffix in ("ing", "ers", "er", "ed", "s"):
        if piece.endswith(suffix) and len(piece) > len(suffix) + 1:
            return [piece[:-len(suffix)], suffix]
    return [piece]


def subword_tokens(text: str) -> list[str]:
    out = []
    for piece in word_tokens(text):
        out.extend(_split_suffix(piece))
    return out


def build_vocab(texts=TRAIN_TEXT) -> list[str]:
    ordinary = sorted({piece for text in texts for piece in word_tokens(text)})
    return [*SPECIAL_TOKENS, *ordinary]


def encode(text: str, vocab: list[str], max_length: int = 8):
    if max_length < 2:
        raise ValueError("max_length must leave room for BOS and EOS")
    stoi = {token: index for index, token in enumerate(vocab)}
    body = [stoi.get(piece, stoi["<unk>"]) for piece in word_tokens(text)]
    body = body[: max_length - 2]
    ids = [stoi["<bos>"], *body, stoi["<eos>"]]
    mask = [1] * len(ids)
    pad_count = max_length - len(ids)
    ids.extend([stoi["<pad>"]] * pad_count)
    mask.extend([0] * pad_count)
    return ids, mask


def byte_tokens(text: str) -> list[int]:
    return list(text.encode("utf-8"))


def byte_decode(values: list[int]) -> str:
    return bytes(values).decode("utf-8")


def lookup_embeddings(ids: list[int], table=EMBEDDING_TABLE) -> list[list[float]]:
    vectors = []
    for token_id in ids:
        if token_id < 0 or token_id >= len(table):
            raise IndexError("token id is outside the embedding table")
        vectors.append(list(table[token_id]))
    return vectors


def attach_positions(ids: list[int], mask: list[int]) -> list[tuple[int, int]]:
    if len(ids) != len(mask):
        raise ValueError("ids and mask must have the same length")
    return [(token_id, position) for position, (token_id, valid) in enumerate(zip(ids, mask)) if valid == 1]


def unknown_rate(text: str, vocab: list[str]) -> float:
    pieces = word_tokens(text)
    known = set(vocab)
    if not pieces:
        return 0.0
    return sum(piece not in known for piece in pieces) / len(pieces)


def evaluate_cases(vocab: list[str]) -> dict[str, dict[str, float | int]]:
    results = {}
    for name, text in EVAL_CASES.items():
        results[name] = {
            "word_tokens": len(word_tokens(text)),
            "subword_tokens": len(subword_tokens(text)),
            "byte_tokens": len(byte_tokens(text)),
            "unknown_rate": round(unknown_rate(text, vocab), 3),
        }
    return results


def build_report() -> dict:
    vocab = build_vocab()
    stoi = {token: index for index, token in enumerate(vocab)}
    cases = evaluate_cases(vocab)
    worst = max(cases, key=lambda name: (cases[name]["unknown_rate"], name))
    return {
        "vocab_size": len(vocab),
        "special_ids": {token: stoi[token] for token in SPECIAL_TOKENS},
        "cases": cases,
        "worst_unknown_slice": worst,
        "conclusion": (
            "The tiny word vocabulary is compact on familiar training-like text but loses unseen pieces. "
            "UTF-8 bytes preserve every evaluation string, while subword pieces demonstrate how reusable fragments can reduce whole-word dependence."
        ),
    }


if __name__ == "__main__":
    from pprint import pprint
    pprint(build_report())
