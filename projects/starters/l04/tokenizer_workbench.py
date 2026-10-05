"""Starter for p04-tokenizer-workbench.

Complete the TODO functions without looking at the reference solution.
The fixtures are deterministic and use only Python's standard library.
"""

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
    """Split text into lowercase Unicode word/punctuation pieces."""
    # TODO: return deterministic word-like pieces.
    return []


def subword_tokens(text: str) -> list[str]:
    """Split alphabetic words with a few reusable suffix pieces."""
    # TODO: reuse suffixes such as ing/ers/er/ed/s when present.
    return []


def build_vocab(texts=TRAIN_TEXT) -> list[str]:
    """Return SPECIAL_TOKENS followed by sorted ordinary word pieces."""
    # TODO: preserve the special-token IDs exactly.
    return list(SPECIAL_TOKENS)


def encode(text: str, vocab: list[str], max_length: int = 8):
    """Return (ids, mask), preserving BOS/EOS and padding/truncating safely."""
    # TODO: use <unk> for missing pieces, keep BOS/EOS, and pad with <pad>.
    return [], []


def byte_tokens(text: str) -> list[int]:
    """Return UTF-8 byte IDs for text."""
    # TODO
    return []


def byte_decode(values: list[int]) -> str:
    """Decode UTF-8 byte IDs back to text."""
    # TODO
    return ""


def lookup_embeddings(ids: list[int], table=EMBEDDING_TABLE) -> list[list[float]]:
    """Look up one vector per token ID and fail clearly for invalid IDs."""
    # TODO
    return []


def attach_positions(ids: list[int], mask: list[int]) -> list[tuple[int, int]]:
    """Return (token_id, position) pairs for real (mask=1) positions."""
    # TODO
    return []


def unknown_rate(text: str, vocab: list[str]) -> float:
    """Fraction of word pieces that are missing from vocab."""
    # TODO
    return 0.0


def evaluate_cases(vocab: list[str]) -> dict[str, dict[str, float | int]]:
    """Evaluate fixed slices with word/subword/byte token counts and unknown rate."""
    # TODO
    return {}


def build_report() -> dict:
    """Return a deterministic summary used by the project validator."""
    # TODO
    return {
        "vocab_size": None,
        "special_ids": None,
        "cases": None,
        "worst_unknown_slice": None,
        "conclusion": "TODO",
    }


if __name__ == "__main__":
    from pprint import pprint
    pprint(build_report())
