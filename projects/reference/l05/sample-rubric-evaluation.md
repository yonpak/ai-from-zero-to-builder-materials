# Sample rubric evaluation — p05-mini-transformer reference

Reference: `projects/reference/l05/reference_solution.py`

| Criterion | Score | Evidence |
|---|---:|---|
| Scaled causal multi-head attention | 4/4 | Validator checks head splitting, scaled scores through the implementation path, normalized rows, zero future mass, and divisibility failure. |
| Residual/norm/MLP block | 4/4 | Pre-norm attention and feed-forward updates both return to the residual width; block shape is asserted. |
| Stacking and full architecture | 4/4 | Repeated blocks preserve `(T,C)`; final model returns `(T,V)` logits from deterministic token/position embeddings. |
| Debugging and evaluation | 4/4 | `width=6,n_head=4` fails early; prefix invariance detects future leakage even when shapes remain valid. |
| Reproducibility and communication | 4/4 | Python 3.11+ standard library only; no network, dataset, model download, secret, or random state. |

**Total: 20/20.**

The reference earns full credit because it demonstrates the required Level 5 semantics and evidence. It is intentionally small: performance optimization and training are deferred to Level 6.
