# p07 Reference Evidence

The reference package demonstrates the deterministic reduced acceptance path for **p07-reliable-llm-workflow**.

- `reference_solution.py` implements retrieval, structured provenance validation, fixed-case evaluation, and run-package validation.
- `sample-run/workflow-run.json` is the passing reference record.
- `failure-run/workflow-run.json` deliberately cites a source that was not supplied to the request and must be rejected.

This package tests workflow contracts. It does not claim that a recorded fixture substitutes for live-model quality evaluation.
