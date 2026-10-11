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

## Judgment questions

Ask yourself, and locate a trace or measurement for each answer:

- Do chunks preserve the evidence the task requires? If not, show the lost span and revise the chunking choice.
- Do lexical, vector, or hybrid choices match the actual query types? If not, compare a failure slice.
- Does reranking improve the intended slices, not just aggregate scores? If not, inspect per-slice metrics.
- Does each citation substantiate its claim? If not, correct or abstain from the claim.
- Are freshness and deletion behavior recorded? If not, document the update boundary.
- Did you locate the earliest failed boundary? If not, trace authorization → retrieval → ranking → generation.

## Assessment guardrail

A live vector database or model API is optional for repository acceptance. If provided, it extends the evidence but does not replace deterministic provenance, authorization, and evaluation checks.

## Self-check before you call it done

- Can you trace corpus versions, chunk/index IDs, retrieval/reranking settings, and freshness/deletion behavior?
- Can you prove tenant/active filtering happened before ranking and that each cited claim uses an authorized, supplied source?
- Can you reproduce recall@2, grounded-answer accuracy, abstention, unauthorized-exposure count, and the release decision?
- Can you reproduce the cross-tenant failure and diagnose the earliest failed boundary with a focused remedy?
