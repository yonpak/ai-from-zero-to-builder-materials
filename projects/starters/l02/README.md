# p02-neural-net-from-scratch — Neural Network From Scratch

Build and explain a tiny two-layer neural network using NumPy and explicit gradients.

## Prerequisites

Python help for this project:

- [P2 — NumPy Arrays and Shapes](https://aizero.ruzincompany.com/learn/01-level-1/numpy-arrays-and-shapes)
- [P3 — Writing Small Python Functions](https://aizero.ruzincompany.com/learn/01-level-1/writing-small-python-functions)

Complete Level 2 through **L2.15 — Neural Network Debugging Workshop**. The canonical project depends on `p01-trustworthy-ml`, so you should already know how to make fair train/validation comparisons and avoid leakage.

## Goal

Starting from the provided scaffold, make a small XOR network learn by implementing the missing backward/update logic. Then use evidence to debug one intentional failure.

## Deliverables

1. `network.py` with a two-layer forward pass and your backward/update implementation.
2. `train.py` that produces a reproducible training record.
3. A short `REPORT.md` that includes:
   - the shape of every parameter and activation;
   - starting and ending loss;
   - final XOR predictions;
   - one gradient check or hand-derived gradient check;
   - one intentional failure, the evidence you observed, and the fix;
   - one paragraph explaining why nonlinearity is required.
4. The output from the submission checker.

## Setup

This project uses Python 3 and NumPy only.

```bash
python projects/starters/l02/train.py
```

The untouched starter is expected to run successfully but **not learn**: `backward_and_step` is a visible TODO. That is the starting state, not a hidden failure.

After completing the TODO, validate your work with:

```bash
python projects/tests/l02/check_submission.py projects/starters/l02
```

The checker tests behavior, not exact floating-point bytes.

## Expected success evidence

A completed implementation should reduce loss substantially and reach all four XOR predictions correctly with the fixed seed and default settings.

## Intentional failure/debug path

After your correct run, set the learning rate to an excessively large value such as `5.0`. Record what happens to loss or parameters. Restore the stable value, explain why the large step was unsafe, and include the evidence in `REPORT.md`.

## Reproducibility

Keep the provided random seed. If you change it, record the new seed and compare results. Do not use hidden test data or external services.

## Data provenance

The XOR dataset is generated directly in the repository from the four binary input pairs. It contains no external data and requires no credentials.

## Compare with a reference (optional)

Try the TODOs yourself and run the submission validator first. Then inspect the [published reference solution](../../reference/l02/network_reference.py) and any example evaluations. To verify the published reference against its acceptance tests from the public materials repository root, run:

```bash
python projects/tests/l02/test_reference.py
```

This command tests the reference, **not your own solution**. Use the project rubric and submission checker to evaluate your implementation.
