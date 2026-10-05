#!/usr/bin/env python3
"""Objective validator for p04-tokenizer-workbench learner submissions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("p04_submission", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load submission: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def validate(module):
    require(module.word_tokens("Cats nap.") == ["cats", "nap", "."], "word_tokens should split words and punctuation deterministically")
    require(module.subword_tokens("players played") == ["play", "ers", "play", "ed"], "subword_tokens should reuse the fixture suffix pieces")

    vocab = module.build_vocab()
    require(vocab[:4] == module.SPECIAL_TOKENS == ["<pad>", "<unk>", "<bos>", "<eos>"], "special tokens must occupy fixed IDs 0..3")
    require(vocab == module.build_vocab(), "vocabulary construction must be deterministic")

    ids, mask = module.encode("tiny quokka", vocab, max_length=6)
    require(len(ids) == len(mask) == 6, "encode should return fixed-length ids and mask")
    require(ids[0] == 2 and ids[3] == 3, "encoded fixture should preserve BOS and EOS")
    require(ids[2] == 1, "unseen quokka should use <unk> id 1")
    require(mask == [1, 1, 1, 1, 0, 0], "padding mask should mark only real positions")
    require(ids[-2:] == [0, 0], "padding should use <pad> id 0")

    long_ids, long_mask = module.encode("tiny models predict tokens play players", vocab, max_length=5)
    require(long_ids[0] == 2 and long_ids[-1] == 3, "truncation must preserve BOS and EOS")
    require(long_mask == [1, 1, 1, 1, 1], "fully occupied truncated sequence should have all-one mask")

    sample = "Token🙂"
    byte_ids = module.byte_tokens(sample)
    require(byte_ids and all(isinstance(value, int) and 0 <= value <= 255 for value in byte_ids), "byte_tokens should return byte integers")
    require(module.byte_decode(byte_ids) == sample, "byte representation should round-trip UTF-8 text")

    small_ids, small_mask = module.encode("tiny", vocab, max_length=5)
    vectors = module.lookup_embeddings(small_ids)
    require(len(vectors) == len(small_ids), "embedding lookup should return one vector per ID")
    require(all(len(vector) == len(module.EMBEDDING_TABLE[0]) for vector in vectors), "embedding width must be consistent")
    positions = module.attach_positions(small_ids, small_mask)
    require(positions == [(small_ids[0], 0), (small_ids[1], 1), (small_ids[2], 2)], "positions should align only with mask=1 tokens")

    require(module.unknown_rate("tiny models", vocab) == 0.0, "familiar fixture should have zero unknown rate")
    require(module.unknown_rate("quokka predicts", vocab) > 0.0, "rare-name fixture should expose unknown coverage failure")

    cases = module.evaluate_cases(vocab)
    require(set(cases) == set(module.EVAL_CASES), "evaluate_cases should return every fixed evaluation slice")
    require(cases["familiar"]["unknown_rate"] == 0.0, "familiar slice should be covered")
    require(cases["rare_name"]["unknown_rate"] > 0.0, "rare_name slice should expose the intentional failure")
    require(cases["emoji"]["byte_tokens"] > 0, "byte metric should cover emoji text")

    report = module.build_report()
    for key in ("vocab_size", "special_ids", "cases", "worst_unknown_slice", "conclusion"):
        require(key in report, f"report is missing {key}")
    require(report["special_ids"] == {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}, "report should preserve special-token contract")
    require(report["worst_unknown_slice"] in {"emoji", "multilingual", "rare_name"}, "worst slice should be one of the held-out failure slices")
    require(isinstance(report["conclusion"], str) and len(report["conclusion"].strip()) >= 80, "write a meaningful evidence-based conclusion")


def main(argv):
    if len(argv) != 2:
        print("Usage: python projects/tests/l04/validate_submission.py PATH_TO_TOKENIZER_WORKBENCH.py", file=sys.stderr)
        return 2
    path = Path(argv[1]).resolve()
    if not path.is_file():
        print(f"Submission not found: {path}", file=sys.stderr)
        return 2
    try:
        validate(load_module(path))
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: p04-tokenizer-workbench objective checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
