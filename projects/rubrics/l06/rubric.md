# p06-tiny-llm Rubric — Train and Ship a Tiny LLM

Score each criterion from **0–4**. A submission should score at least **16/20** overall and must not score 0 on reproducibility or debugging.

| Criterion | 4 — Strong evidence | 3 — Meets | 2 — Partial | 1 — Weak | 0 — Missing |
|---|---|---|---|---|---|
| End-to-end language-model workflow | Correct next-token/data/model/training story; training evidence is finite and tied to a decoder-only configuration; selected checkpoint is justified | Complete workflow with minor gaps | Some stages evidenced but important connection missing | Mostly description without run evidence | No credible training workflow |
| Evaluation and controllable sampling | Held-out loss plus fixed prompt samples; decoding settings recorded; controlled comparison changes one factor; limitations stated | Uses held-out metric and fixed samples with settings | Evaluation present but comparison/provenance weak | One cherry-picked sample or train loss only | No evaluation |
| Failure analysis and debugging | Reproduces a concrete failure, separates evidence/hypothesis, makes one focused fix/check, records result and next implication | Complete failure/debug trace | Failure shown but cause/evidence reasoning incomplete | Vague “fixed it” note | No failure/debug path |
| Reproducibility and packaging | Seed, config, tokenizer/checkpoint fingerprints, environment, commands, artifact provenance, metrics, samples, and reduced validation path all align; no secrets | Package can be restored/reviewed with small omissions | Important metadata missing or ambiguous | Mostly an unlabeled artifact | Missing package or secrets committed |
| Communication and engineering judgment | Explains tensor/data contracts, resource expectations, what evidence proves, what it does not prove, and next test | Clear report with sensible tradeoffs | Understandable but shallow tradeoff reasoning | Mostly output dump | No explanation |

## Exit-skill mapping

- **Train a tiny decoder-only LM end to end:** End-to-end workflow.
- **Diagnose loss/generation failures:** Failure analysis and debugging; evaluation.
- **Sample controllably:** Evaluation and controllable sampling.
- **Package a reproducible run:** Reproducibility and packaging.

## Objective checks

The repository validator verifies the reduced-path functions, required run metadata, compatible tokenizer/checkpoint fingerprints, fixed sample records, valid configuration shapes, and intentional failure rejection. Human review scores whether the actual training/evaluation evidence and explanations are technically convincing.

## Assessment guardrail

Generated text does not need to match the reference sample. Tiny model quality is intentionally limited. The rubric rewards controlled evidence, correct contracts, debugging, and reproducibility rather than fluent prose alone.
