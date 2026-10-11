# p00 Data Detective — strong Core evidence report (example)

> **Format example only.** This shows how to support rubric claims, not a submission to copy. **Use your own numbers and your own observations.** Run L0.12 yourself before filling in the [Core report template](CORE_REPORT_TEMPLATE.md).

## Prediction task and information boundary

- **Lab:** L0.12, canonical browser Lab `labs/browser/l00-12/starter.py` (Core, no terminal validator).
- **Feature:** the numeric input; **label:** the true Boolean outcome. The rule predicts `True` when `value >= threshold`. A prediction is not a known label.
- **Training rows:** `(1,F), (2,F), (3,T), (4,T), (5,T)`. **Held-out rows:** `(2,F), (3,T), (4,T), (6,T)`. The training labels have a `True` majority (3 of 5), so the majority baseline predicts `True` for every held-out row.
- The held-out set should not be used to repeatedly choose the rule. This Lab deliberately reuses those four rows for debugging; after this experiment, a fresh test set would be required for an unbiased final estimate.

## Reproducible Lab evidence

Run the untouched Lab, then change **only** `candidate_threshold = 3` to `candidate_threshold = 2` and rerun.

| Lab run | `debug_record["change"]` | `before` | `after` | `baseline` |
|---|---|---:|---:|---:|
| Unchanged starter | `threshold 4 -> 3` | 1 | 0 | 1 |
| One-line experiment | `threshold 4 -> 2` | 1 | 1 | 1 |

These are **mistake counts**, not accuracy scores, on the same four held-out examples. Threshold 4 wrongly predicts `False` at input 3; threshold 3 fixes that and makes zero mistakes. The baseline makes one mistake (input 2), so threshold 3 beats it on these four examples.

## Intentional failure / focused debug record

- **Prediction before rerun:** lowering the candidate threshold to 2 will change input `2` from `False` to `True`, contradicting its `False` label.
- **Observed failure:** `after` rises from 0 to 1 for threshold 2; `before=1` and `baseline=1` remain unchanged.
- **Hypothesis:** the candidate boundary is now too low, causing one false positive at input 2.
- **Single check:** compare `predict(2, 2)` with the held-out label `False`; no other row, helper, or threshold is changed.
- **Result / next step:** the single error is explained; restore candidate threshold 3, then evaluate on new held-out inputs rather than optimizing against these same four rows.

## Evidence-backed conclusion

**Observation:** threshold 3 makes 0/4 mistakes, while the training-majority baseline and threshold 2 each make 1/4. **Interpretation:** threshold 3 is the best of the tested rules on this tiny held-out set, not necessarily for a new population. Four synthetic examples cannot estimate deployment reliability or rule out distribution shift. Next I would freeze the rule, obtain new labeled cases near the boundary, and measure errors without further tuning on their answers.

**Self-score prompt:** In the 100-point rubric, can I point to all five evidence areas (features/labels, fair boundary, baseline, debugging, reproducibility) before assigning 18–20 in each?
