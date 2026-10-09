# p05-mini-transformer — Build a Mini Transformer

## Goal
Build a deterministic decoder-style mini Transformer from understandable pieces and prove the invariants that make it causal and composable.

## Prerequisites
Complete Level 5 through **L5.16 — Mini Transformer Integration Workshop**. You should be able to explain Q/K/V roles, dot-product scaling, softmax attention weights, causal masks, multiple heads, residual connections, LayerNorm, feed-forward networks, and stacked Transformer blocks.

The canonical cumulative dependency is the Level 4 project **Tokenizer Workbench**. This Level 5 package accepts integer token IDs directly so it remains independently reproducible.

## Setup
Use Python 3.11+ from the repository root. The objective project validator uses only Python's standard library; no network, model download, GPU, secret, or credential is required.

## Your task
Complete the TODOs in `projects/starters/l05/mini_transformer.py`.

Your mini Transformer must:
1. implement numerically stable softmax;
2. normalize each token's feature vector;
3. implement scaled **causal multi-head self-attention** with future probability exactly zero;
4. reject an embedding width that is not divisible by the head count;
5. preserve residual-stream shape through attention, feed-forward, and stacked blocks;
6. assemble token + position embeddings, stacked blocks, final normalization, and vocabulary logits;
7. keep earlier logits unchanged when only future token IDs change;
8. expose attention weights so causal behavior can be inspected.

## Required deliverables
- completed `mini_transformer.py`;
- output from the objective validation command;
- `debug-note.md` describing one intentional failure with evidence, hypothesis, one focused check/change, result, and next step;
- a short architecture note tracing shapes from token IDs `(T)` to residual stream `(T,C)` to logits `(T,V)`;
- a paragraph explaining why a shape-correct model can still be causally wrong.

## Validation
Run:

```bash
python projects/tests/l05/validate_submission.py projects/starters/l05/mini_transformer.py
```

Expected success evidence:

```text
PASS: p05-mini-transformer objective checks
```

## Intentional failure/debug path
Set `width=10` and `n_head=3`. A correct implementation must fail early with a clear divisibility error. Then restore a divisible width.

A second failure check changes only future token IDs. If logits at earlier positions change, the attention mask is wrong even when every tensor/list shape looks correct.

## Reproducibility and provenance
The model uses deterministic teaching embeddings and standard-library math. There is no external dataset, pretrained model, internet access, secret, or random initialization. Stage B PyTorch notebooks in `labs/notebooks/level-05/` provide the framework-backed bridge after these semantics are understood.
