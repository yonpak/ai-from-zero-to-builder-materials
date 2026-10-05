# p06-tiny-llm — Train and Ship a Tiny LLM

## Goal

Train or reuse the validated Level 6 tiny decoder-only language-model path, evaluate it on fixed evidence, diagnose one failure, and ship a reproducible run package that another learner can inspect.

## Prerequisites

Complete Level 6 through **L6.14 — Tiny LLM Integration Workshop**. The canonical cumulative project dependency is the Level 5 project **Build a Mini Transformer**.

You should be able to:
- create next-token input/target windows without leakage;
- reason about `(B, T, C)` hidden states and `(B, T, V)` logits;
- train the validated tiny decoder-only model and read train/validation loss;
- save configuration/checkpoint identity and seed information;
- sample with controlled decoding settings;
- recognize repetition/collapse/incoherence and debug with evidence.

## Two execution paths

### Full training evidence

Use the frozen canonical Stage B `lab-l06-06` notebook or your own equivalent Level 6 implementation. CPU is supported by the teaching configuration; GPU is optional. Export the selected checkpoint/run evidence rather than committing a large binary checkpoint.

### Deterministic reduced review path

The project code, validator, and sample run use only Python 3.11+ standard-library features. Reviewers can verify evaluation, failure/debug, provenance, and packaging contracts without retraining the model.

## Setup

From the repository root:

```bash
python --version
python projects/tests/l06/validate_submission.py \
  projects/starters/l06/run_package.py \
  path/to/your/run.json
```

If you use `uv`, the starter includes a dependency-free `pyproject.toml` for the reduced path:

```bash
uv run python projects/tests/l06/validate_submission.py \
  projects/starters/l06/run_package.py \
  path/to/your/run.json
```

No credential is required. `.env.example` is intentionally empty of secrets.

## Your task

Complete the TODOs in `run_package.py` and produce a `run.json` from your training/evaluation evidence.

Your implementation must provide:
1. `perplexity(loss)` for positive finite average natural-log loss;
2. `repeated_bigram_rate(text)` as a simple generation-failure indicator;
3. `choose_best(records)` selecting the lowest validation-loss record;
4. `validate_run(data)` rejecting missing or inconsistent reproducibility evidence.

Your `run.json` must include:
- `run_id` and integer `seed`;
- model `config` including vocabulary/context/model dimensions;
- `tokenizer_fingerprint`;
- `checkpoint_fingerprint` and matching `checkpoint_tokenizer_fingerprint`;
- train/validation loss history or selected validation loss evidence;
- at least two fixed evaluation samples with their prompt/decoding settings;
- `environment` with Python/runtime information;
- `debug_record` containing failure, evidence, hypothesis, focused fix, and result;
- a limitations statement.

## Required deliverables

- completed `projects/starters/l06/run_package.py`;
- your `run.json`;
- a short `PROJECT_REPORT.md` explaining:
  - data/tokenizer provenance;
  - the model configuration;
  - why the selected checkpoint was chosen;
  - one controlled decoding comparison;
  - one failure/debug trace;
  - limitations and what you would test next.

Do not commit secrets or large model binaries. If your checkpoint is stored elsewhere, record a non-secret artifact identity/fingerprint and retrieval note.

## Validation

Expected success evidence:

```text
PASS: p06-tiny-llm objective checks
```

The validator checks objective behavior and run invariants. It does not require your explanatory prose or generated text to match the reference solution byte-for-byte.

## Intentional failure/debug path

`projects/tests/l06/fixtures/failure/run.json` deliberately gives the checkpoint a tokenizer fingerprint that does not match the run tokenizer. The integration checker and project validator must reject it. Fix the artifact pairing or metadata source; do not weaken the check.

## Resource expectations

The reduced path is CPU-only, deterministic, and uses no network. The optional full training path uses the existing tiny teaching model and is designed to be practical on CPU; a GPU may shorten training but is not required for acceptance.

## Provenance

The reduced reference evidence is synthetic teaching data committed in this repository. The full training source is the repository's validated Tiny LLM teaching corpus/notebook package. No external dataset is required for the project acceptance path.
