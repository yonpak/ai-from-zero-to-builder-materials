# p09-evidence-rag Rubric — Evidence-Backed RAG

Score each criterion from **0–4**. A submission should score at least **16/20** overall and must not score 0 on access/provenance or evaluation.

| Criterion | 4 — Strong evidence | 3 — Meets | 2 — Partial | 1 — Weak | 0 — Missing |
|---|---|---|---|---|---|
| Corpus/chunk/index lineage | Source snapshot, chunker, embedding/retrieval identity, updates, and IDs are traceable and reproducible | Clear lineage with minor gaps | Core IDs exist but version/update evidence is incomplete | Mostly an unversioned document dump | No trustworthy corpus/index identity |
| Retrieval and reranking | Candidate retrieval, exact/semantic trade-offs, cutoff, reranking, and failure slices are measured under fixed cases | Reproducible retrieval with minor gaps | Retrieval works but diagnostics or slices are shallow | Only a few anecdotal queries | No coherent retrieval system |
| Access and provenance | Eligibility is enforced before ranking; supplied sources are authorized; supported answers cite supplied evidence | Correct boundaries with minor gaps | Some provenance checks but one important boundary is missing | Prompt wording is the main security control | Unauthorized/unsupplied evidence can be accepted |
| RAG evaluation and failure analysis | Retrieval metrics + grounded-answer metrics + abstention + earliest-boundary debug trace are all present | Complete evaluation with minor gaps | Final-answer evaluation present but retrieval diagnosis weak | Cherry-picked answer samples only | No fixed evaluation |
| Reproducibility and communication | Corpus/retriever/reranker/prompt/generator/evaluator identities, commands, limitations, and optional live-path differences are explicit | Reproducible package with small omissions | Several artifact versions or limitations missing | Mostly screenshots/output dumps | No reproducible package |

## Objective checks

The reduced validator checks:

- tenant/active eligibility filtering before ranking;
- deterministic retrieval over eligible sources;
- grounded-output provenance;
- supplied-source subset relationships;
- recall@2 and grounded-answer accuracy recomputation;
- unauthorized-exposure count;
- release-rule recomputation;
- intentional cross-tenant failure rejection.

## Human review

Human review should inspect whether:

- chunking preserves the evidence needed for the task;
- lexical/vector/hybrid choices match query types;
- reranking improves the intended slices rather than only averages;
- citations actually support claims;
- freshness/deletion behavior is documented;
- failures are diagnosed at the earliest broken boundary.

## Assessment guardrail

A live vector database or model API is optional for repository acceptance. If provided, it extends the evidence but does not replace deterministic provenance, authorization, and evaluation checks.
