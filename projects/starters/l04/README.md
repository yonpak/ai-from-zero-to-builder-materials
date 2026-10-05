# p04-tokenizer-workbench — Tokenizer Workbench

## Goal
Build a deterministic tokenizer workbench that compares simple word, subword-style, and byte representations; handles special tokens and masks; demonstrates embedding/position alignment; and diagnoses at least one realistic tokenizer failure.

## Prerequisites
Complete Level 4 through **L4.14 — Tokenizer Evaluation Workshop**. You should be able to reason about vocabularies, unknown tokens, UTF-8 bytes, subword pieces, special-token IDs, padding/masks, embeddings, positions, context windows, and tokenizer evaluation slices.

The canonical cumulative project dependency is the Level 3 project **Transfer Learning Across a Real Dataset**, but this Level 4 project package is self-contained and does not require copying a Level 3 implementation.

## Setup
No third-party packages are required. Use Python 3.11+ from the repository root.

## Your task
Complete the TODOs in `projects/starters/l04/tokenizer_workbench.py`.

Your workbench must:
1. tokenize text deterministically into word-like pieces;
2. build a vocabulary with fixed `<pad>`, `<unk>`, `<bos>`, and `<eos>` IDs;
3. encode to a fixed context length while preserving BOS/EOS, padding with `<pad>`, and producing a 1/0 mask;
4. provide UTF-8 byte IDs that round-trip to the original text;
5. produce a simple reusable subword segmentation for the supplied training/evaluation examples;
6. look up embedding vectors by token ID and attach explicit sequence positions;
7. evaluate fixed text slices using token count and unknown rate;
8. identify an intentional failure case and write an evidence-based debug note.

## Required deliverables
- completed `tokenizer_workbench.py`;
- output from the objective validation command;
- `debug-note.md` containing: failing input, observed pieces/IDs, hypothesis, one focused check/change, result, and next step;
- a 6–10 sentence decision note comparing the word, subword-style, and byte representations for the supplied evaluation slices;
- one paragraph explaining how token IDs, embedding rows, positions, and context length must stay aligned.

## Validation
From the repository root, run:

```bash
python projects/tests/l04/validate_submission.py projects/starters/l04/tokenizer_workbench.py
```

Expected success evidence:

```text
PASS: p04-tokenizer-workbench objective checks
```

The validator checks behavior and invariants. Your explanatory wording does not need to match the reference solution.

## Intentional failure/debug path
The case `EVAL_CASES["rare_name"]` contains a word outside the tiny training vocabulary. The simple word tokenizer should expose information loss through `<unk>`. Compare it with byte and subword-style behavior instead of hiding the failure.

A valid debug note should separate:
- **evidence** — exact pieces, IDs, mask, or metric;
- **hypothesis** — why the failure happened;
- **focused check/change** — one controlled action;
- **result** — what changed or stayed the same;
- **next step** — what evidence you would gather next.

## Reproducibility and provenance
All teaching text is deterministic and committed directly in the starter. There is no external dataset, model download, network call, secret, or credential. The validation path uses only Python's standard library.
