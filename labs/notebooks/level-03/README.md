# Level 3 Stage B notebooks

These notebooks implement canonical Labs `lab-l03-11` through `lab-l03-14`.

- Runtime family: Stage B (Colab/Kaggle-compatible notebook).
- Default execution: CPU-first; GPU optional and unnecessary.
- Python: 3.11+.
- Dependency ranges: NumPy 1.26–2.x, scikit-learn 1.5–1.x, PyTorch 2.x.
- Seed: 13.
- Dataset: `sklearn.datasets.load_digits`, bundled with scikit-learn; no network download or credentials.
- Target split: deterministic and shared where comparisons are made.

Run notebooks from top to bottom. Do not reuse mutated model state between controlled comparisons; rebuild from the fixed source/frozen checkpoint.
