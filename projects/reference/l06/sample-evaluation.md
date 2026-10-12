# Sample Rubric Evaluation — p06-tiny-llm

This example shows how to use the rubric; it is not a required wording template.

| Criterion | Score | Evidence |
|---|---:|---|
| End-to-end language-model workflow | 3/4 | Uses the validated Level 6 training path and records a compatible decoder-only configuration/checkpoint. The committed reduced record does not itself retrain the model, so a learner seeking 4/4 should attach their full training evidence. |
| Evaluation and controllable sampling | 4/4 | Records held-out validation loss, two fixed prompts, explicit temperature/top-k/top-p/seed, and a limitations statement. |
| Failure analysis and debugging | 4/4 | Names a repetition failure, records evidence and hypothesis, changes one decoding factor, and records the result. |
| Reproducibility and packaging | 4/4 | Config, seed, tokenizer/checkpoint fingerprints, environment, samples, validation loss, and deterministic review commands align. |
| Communication and engineering judgment | 3/4 | Clearly separates the reduced review path from full training and states model-scale limitations; a learner report can add more tensor/data-contract explanation. |

**Total: 18/20 — meets the project threshold.**

The intentional failure fixture should receive a blocking reproducibility finding because its tokenizer and checkpoint tokenizer fingerprints differ. A reviewer should not award points for making the validator accept inconsistent artifacts.
