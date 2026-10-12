# p08 Reference Evidence

This reference package demonstrates the deterministic reduced acceptance path for **p08-adapt-small-llm**.

- `reference_solution.py` implements LoRA parameter counting, group-safe splitting, release rules, preference-method context checks, and adaptation-run validation.
- `sample-run/adaptation-run.json` is the passing record.
- `failure-run/adaptation-run.json` intentionally contains a base/adapter lineage mismatch and unacceptable retention regression.

The run records also encode a structured RLHF-versus-DPO route contract, require the selected optimization route to match it, and link independent evaluation IDs to the recorded target and retention metrics while keeping any preference/reward proxy ID separate. The reduced path validates engineering and evidence contracts. It does not claim to substitute for live-model fine-tuning or preference-optimization quality evaluation.
