# Level 6 Lab Reproducibility

## Browser labs

`lab-l06-01` through `lab-l06-05` and `lab-l06-07` through `lab-l06-12` run directly in the website with Pyodide. They use only the Python standard library, so a notebook launcher would add unnecessary sign-in and tab-switching friction.

Each browser lab keeps learner-visible code separate from hidden `unittest` checks. Exploratory labs without a TODO pass immediately and treat Lesson-directed edits as experiments rather than errors. Labs with a TODO still fail until the learner implements the requested behavior; after that, an exploratory Lab can accept controlled experiment edits while keeping its invariants fixed.

`lab-l06-06` is intentionally different. It trains and samples the tiny language model with PyTorch, so it remains the notebook-based training lab under `labs/notebooks/tiny-llm/**`.

The older standard-library notebook source files in this directory are retained as implementation history, but their Stage-B manifests are no longer published or referenced by the curriculum.

## Local integration labs

`lab-l06-13` and `lab-l06-14` are local-Python activities. Run them from the repository root with Python 3.11+:

```bash
python labs/notebooks/level-06/l06-13-package-run.py projects/tests/l06/fixtures/passing
python labs/notebooks/level-06/l06-14-integration-check.py projects/tests/l06/fixtures/passing
```

Both commands use only the Python standard library. They validate small committed metadata/evidence and do not require a GPU, network access, secrets, or a large checkpoint.

For the full model-training experience, use `lab-l06-06`. The Level Project combines its training evidence with the deterministic local package/evaluation checks.

## Website representation

Browser labs are published through the shared web lab registry. Local activities remain outside the browser and are published through `labs/local/registry.json`, where the shared `<Lab>` component renders an explicit local-run card.
