# p05-mini-transformer Rubric

Project ID: `p05-mini-transformer`  
Launch: after `l05-16-mini-transformer-integration-workshop`  
Canonical dependency: `p04-tokenizer-workbench`

Score each criterion 0–4. A strong submission earns at least 16/20 and has no zero in Causality or Reproducibility.

| Criterion | Level 5 exit-skill mapping | 4 — Strong evidence | 2 — Partial evidence | 0 — Missing/incorrect |
|---|---|---|---|---|
| Scaled causal multi-head attention | Implement scaled causal MHA | Scores are scaled, heads split/rejoin correctly, rows normalize, future mass is zero, divisibility checked | Attention mostly works but one invariant is weak or untested | Future leakage or no multi-head implementation |
| Residual/norm/MLP block | Explain and implement residual/norm/MLP roles | Pre-norm residual paths preserve shape and MLP is position-wise with explicit checks | Components exist but ordering/role explanation is incomplete | Block contract is absent or shape-invalid |
| Stacking and full architecture | Assemble and stack Transformer blocks | Embeddings → stack → final norm → vocabulary logits are traced and depth preserves `(T,C)` | Complete path exists but shape reasoning is weak | No complete mini Transformer |
| Debugging and evaluation | Debug shape/mask errors | Intentional divisibility and future-leakage failures are reproduced; evidence → hypothesis → focused fix is clear | One failure is shown without strong causal evidence | Only happy-path output |
| Reproducibility and communication | Reproduce and explain | Standard validator passes from clean Python 3.11+, no network/secrets, architecture and causal reasoning are clear | Runs with undocumented assumptions or weak explanation | Cannot reproduce or relies on unrecorded external state |

## Required evidence
- objective validator output;
- architecture shape note;
- causal prefix-invariance evidence;
- future-attention-mass evidence;
- intentional failure/debug note;
- short explanation of why attention mixes positions while the feed-forward network acts position-wise.

Human review should reward reasoning and observable evidence, not byte-identical prose.
