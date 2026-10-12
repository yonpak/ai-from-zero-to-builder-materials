# p09 Reference Evidence

The reference package demonstrates the deterministic reduced acceptance path for **p09-evidence-rag**.

- `reference_solution.py` implements eligibility filtering, retrieval, grounded-output validation, and run-package validation.
- `sample-run/rag-run.json` is the passing reference record.
- `failure-run/rag-run.json` deliberately exposes a cross-tenant source and must be rejected.

This package validates RAG workflow contracts. It does not claim that lexical-overlap fixtures substitute for live vector-search or generator-quality evaluation.
