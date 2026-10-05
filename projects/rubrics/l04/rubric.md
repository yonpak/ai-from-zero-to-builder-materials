# p04-tokenizer-workbench rubric

Total: **100 points**. A suggested passing threshold is **80** with no zero in a critical contract criterion.

| Criterion | Points | Observable evidence | Level 4 exit-skill mapping |
|---|---:|---|---|
| Deterministic tokenization and vocabulary | 15 | Word-like splitting is deterministic; special tokens are fixed; repeated vocabulary builds match | implement/evaluate simple tokenizers |
| Subword and byte representations | 15 | Subword-style reuse is demonstrated; UTF-8 byte path round-trips varied text | implement/evaluate simple/subword tokenizers |
| Special tokens, padding, truncation, masks | 20 | BOS/EOS preserved; `<unk>` visible; padding and 1/0 mask align; truncation keeps sequence contract | handle special tokens/masks |
| Embedding and position alignment | 15 | IDs select valid vectors; one vector per ID; real positions align with mask and sequence order | explain embeddings/positions |
| Context/evaluation reasoning | 15 | Decision note discusses token-count/context implications and compares fixed slices/metrics | explain context windows; evaluate tokenizers |
| Failure analysis and debugging | 10 | Intentional rare/unfamiliar input is reproduced; evidence, hypothesis, focused check, result, next step are recorded | diagnose tokenizer failures |
| Reproducibility and communication | 10 | Objective validator passes; no external secret/data dependency; decision/limitation is clear and evidence-backed | reproducible evaluation and explanation |

## Performance anchors

### 90–100 — Strong
The workbench passes objective checks, preserves all tokenizer contracts, compares representations on every required slice, and explains tradeoffs and the failure case with concrete evidence. The decision note states limitations instead of claiming a universally best tokenizer.

### 80–89 — Ready
Core behavior is correct and reproducible. Evaluation and debugging are present, with only minor gaps in explanation or additional evidence.

### 60–79 — Partial
Some tokenizer functions work, but one important contract such as masks, special IDs, byte round-trip, or evaluation coverage is incomplete. Explanations may describe results without tracing causes.

### Below 60 — Not yet
The submission is not reproducible, hides or ignores failure cases, or has fundamental representation-contract errors that make encoded data unreliable.

## Critical zero conditions
A submission cannot be considered Level 4 complete if any of these are true:
- special-token meanings are not stable;
- encoded sequence and mask lengths disagree;
- UTF-8 byte path cannot reproduce the supplied text;
- objective validator cannot run from a clean Python 3.11+ environment;
- the intentional failure/debug scenario is omitted rather than investigated.
