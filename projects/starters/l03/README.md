# p03-transfer-learning — Transfer Learning Across a Real Dataset

Adapt a small pretrained encoder to a related target task on the scikit-learn handwritten-digits dataset. Compare three strategies under the **same** target split and metric: scratch training, frozen transfer, and controlled fine-tuning.

## Prerequisites

Complete Level 3 through **L3.14 — Adaptation Review: Choose, Fine-Tune, Explain**. The canonical project depends on `p02-neural-net-from-scratch`, so you should already be able to reason about tensor shapes, training curves, gradients, and reproducible comparisons.

## Dataset and task

The project uses `sklearn.datasets.load_digits`, a bundled copy of the UCI Optical Recognition of Handwritten Digits dataset. No network download, account, secret, or API key is required.

- Source task: predict digit identity (10 classes).
- Target task: predict whether a digit belongs to `{0, 6, 8, 9}` (loop-like digits) or the other digits.
- Target training budget: 40 labeled examples selected with the fixed seed.
- Validation set: fixed and shared across all strategies.

Dataset provenance and usage terms should be reviewed from the scikit-learn/UCI documentation before redistribution outside this repository.

## Goal

Starting from the provided scaffold:

1. pretrain the source model;
2. complete `build_frozen_transfer`;
3. complete `fine_tune`;
4. compare scratch, frozen transfer, and fine-tuning fairly;
5. add a noisy-image failure slice;
6. intentionally fine-tune with an aggressive learning rate and explain the failure evidence.

## Setup

Use Python 3.11+ on CPU. A GPU is not required.

```bash
python -m pip install -r projects/starters/l03/requirements.txt
python projects/starters/l03/adaptation.py
```

The untouched starter is expected to run successfully and stop at two visible `NotImplementedError` TODOs after showing the source and scratch baselines. That is the intended clean-start state.

After completing the TODOs:

```bash
python projects/tests/l03/check_submission.py projects/starters/l03
```

## Deliverables

1. Completed `adaptation.py`.
2. `REPORT.md` based on `REPORT_TEMPLATE.md`.
3. Checker output.
4. A strategy decision that uses at least three pieces of evidence.

Your report must include source-task accuracy; scratch, frozen-transfer, and fine-tuned target accuracy; trainable parameter counts; encoder movement; clean/noisy-slice accuracy; the aggressive-learning-rate failure; provenance notes; and a final strategy decision.

## Expected success evidence

A reasonable completed solution under the fixed seed should exceed 0.80 source-task validation accuracy and 0.75 target accuracy for all three strategies, keep the frozen encoder unchanged, show controlled movement during fine-tuning, and show substantially larger movement under the aggressive failure. Exact floating-point values are not required.

## Intentional failure/debug path

Run fine-tuning again from the **same frozen checkpoint** with `lr=1.0`. Record encoder movement and validation accuracy, compare them with conservative `lr=0.01`, explain why completion alone is not success evidence, and restore the frozen checkpoint before each retry.

## Reproducibility

- Seed: `13`.
- CPU-first; GPU optional but unnecessary.
- Dataset is bundled with scikit-learn.
- No environment variables or credentials are required.
- Keep the fixed train/validation split in the starter.
- Record versions with `python --version` and `pip freeze | grep -E 'torch|scikit-learn|numpy'`.
