# Level 3 notebook reproducibility

## Environment

The canonical Stage B manifests declare Python and package compatibility ranges. A CPU runtime is enough for every default teaching run.

Record the actual environment before reporting results:

```bash
python --version
python -m pip freeze | grep -E 'numpy|scikit-learn|torch'
```

## Determinism

- Seed: `13` for Python, NumPy, and PyTorch.
- PyTorch CPU thread count is fixed to one in the teaching notebooks.
- Train/validation split and the 40-example target subset use the same fixed seed.
- Validation examples are not reused for fitting or strategy selection.

Small floating-point differences across compatible builds are acceptable. The expected outputs are threshold- and relationship-based, not byte-identical.

## Data provenance

The notebooks use scikit-learn's bundled handwritten-digits dataset, derived from the UCI Optical Recognition of Handwritten Digits dataset. No network fetch, account, API key, or secret is required. Review the scikit-learn/UCI dataset documentation before redistributing the dataset separately.

## Smoke path

`python labs/notebooks/level-03/smoke_test.py` parses every notebook and executes its code cells in order. The default smoke path is CPU-only and should complete without external services.
