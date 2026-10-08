# p00-data-detective rubric — 100 points

This rubric maps directly to the Level 0 exit skills. **Core and Builder are two evidence paths to the same learning outcome.** You can earn full Level 0 credit on either path. Not having learned local Python or terminal workflow yet does not cost you points. Use this rubric to score your own work.

Accepted evidence paths:

- **Core browser path:** canonical Lesson 0.12 Lab evidence + completed Core Evidence Report;
- **Builder local path:** completed `data_detective.py` + validator evidence + debug/explanation deliverables.

Your work is scored on the reasoning and reproducibility that fit the path you chose. Writing more code does not earn extra conceptual credit.

## 1. Features and labels — 20 points
- **18–20:** Correctly identifies the numeric input as the feature and the Boolean target as the label; explanation clearly distinguishes prediction from label.
- **12–17:** Reasoning is mostly correct but explanation is incomplete or mixes one term.
- **1–11:** Feature/label roles are confused in evidence or prose.
- **0:** No usable evidence.

## 2. Train/test separation and fair evaluation — 20 points
- **18–20:** Explains that the rule is chosen without using final held-out answers; held-out examples are used for evaluation; explains why repeated tuning on final test answers weakens independence.
- **12–17:** Correct boundary with weak explanation, or one minor evaluation mistake that is identified and corrected.
- **1–11:** Test answers guide model selection without recognizing the problem, or the split is not reproducible.
- **0:** No train/test distinction.

## 3. Predictor, baseline, and objective evidence — 20 points
- **18–20 Core:** Correctly records the canonical Lab's before/after/baseline evidence, traces the changed threshold to the changed prediction, and interprets the baseline fairly.
- **18–20 Builder:** Objective validator passes; model and majority baseline are evaluated on the same held-out examples; result is interpreted correctly.
- **12–17:** Predictor evidence and baseline are present with one small defect or incomplete interpretation.
- **1–11:** A predictor result exists but the comparison is unfair, untraceable, or missing a baseline.
- **0:** No functioning or inspectable predictor evidence.

## 4. Failure analysis and debugging — 20 points
- **18–20:** Learner identifies a specific failure, states a plausible hypothesis, changes or checks one thing at a time, records evidence, and states a next step. The Core path may use the deliberate threshold `3 → 2` unsuccessful change; the Builder path may use `NOISY_TEST_EXAMPLES`.
- **12–17:** Failure is found and partially explained, but cause/evidence/next-step chain is incomplete.
- **1–11:** Failure is hidden, fixed by unrelated changes, or discussed without evidence.
- **0:** No debug attempt.

## 5. Reproducibility and communication — 20 points
- **18–20 Core:** Records the canonical Lesson/Lab, exact one-line edit, before/after/baseline values, observation versus conclusion, and one limitation so another learner can repeat the browser experiment.
- **18–20 Builder:** Provides validation command/output and enough settings/evidence to reproduce the local run; distinguishes observation from conclusion and states one limitation.
- **12–17:** Mostly reproducible evidence with an incomplete record or limitation statement.
- **1–11:** Result depends on undocumented changes or explanation makes claims broader than the evidence.
- **0:** The work cannot be reproduced or explained.

## Performance bands
- **90–100:** Ready to advance; all Level 0 exit skills demonstrated.
- **75–89:** Meets core outcome with one or two specific areas to strengthen.
- **60–74:** Partial mastery; repeat the relevant Lesson/Lab before advancing.
- **0–59:** Major Level 0 skills are missing; revise with rubric evidence.

A passing local validator is required only for the **Builder local path**. It is not a prerequisite for full Level 0 conceptual mastery on the **Core browser path**.