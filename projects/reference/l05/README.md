# Reference package — p05-mini-transformer

`reference_solution.py` is a deterministic standard-library reference for the Level 5 project. It deliberately uses identity Q/K/V projections and deterministic teaching embeddings so the assessment can isolate Transformer semantics without requiring training or external dependencies.

Run:

```bash
python3 projects/tests/l05/validate_submission.py projects/reference/l05/reference_solution.py
python3 projects/tests/l05/test_reference.py
```

The reference demonstrates:
- stable softmax and per-token layer normalization;
- scaled causal multi-head self-attention;
- zero future attention mass;
- residual + feed-forward block composition;
- repeated blocks with preserved shape;
- token/position embedding assembly and vocabulary logits;
- prefix invariance when only future token IDs change;
- a clear failure for incompatible `width`/`n_head`.

This is an evaluation reference, not a claim that identity projections are a production Transformer parameterization.
