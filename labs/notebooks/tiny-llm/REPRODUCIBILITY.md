# Tiny LLM reproducibility notes

- Canonical seed: `7` for model initialization and training batches.
- Sampling examples use an explicit seed (`11` unless a lesson says otherwise).
- Default teaching device: CPU. CUDA is optional and must not be required to understand the lessons.
- Verified implementation target: Python 3.11+ and PyTorch 2.x.
- Tiny corpus: `tiny_corpus.txt`, an original deterministic fixture committed with the notebooks.
- No generated checkpoint is committed. Re-run the training notebook to produce one locally.
- Validation is behavioral rather than byte-for-byte: causal future attention mass must be `0.0`, logits must have the documented shape, loss must remain finite and trend downward on the fixture, and repeated sampling with the same model plus seed must match.
- CPU floating-point values can differ slightly by PyTorch/platform version. Do not treat an exact loss decimal as the success criterion.
