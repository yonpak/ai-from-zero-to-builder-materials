# p09-evidence-rag — Evidence-Backed RAG

## Goal

Build a retrieval-augmented workflow whose evidence path is inspectable:

```text
source snapshot
→ chunk/source identity
→ eligibility filter
→ retrieval ranking
→ supplied evidence
→ grounded output
→ citation/provenance validation
→ retrieval + answer evaluation
→ release decision
```

## Prerequisites

Python help for this project:

- [P3 — Writing Small Python Functions](https://aizero.ruzincompany.com/learn/01-level-1/writing-small-python-functions)
- [P8 — Running Python Projects Locally](https://aizero.ruzincompany.com/learn/06-level-6/running-python-projects-locally)

Complete Level 9 through **RAG System Integration Workshop**. The cumulative project dependency is **Adapt a Small LLM**.

## Canonical reduced path

The repository acceptance path uses Python 3.11+ standard-library code and recorded fixtures. It does **not** require a vector database or live language-model API.

Run:

```bash
python projects/tests/l09/validate_submission.py \
  projects/starters/l09/rag.py \
  path/to/your/rag-run.json
```

Expected success marker:

```text
PASS: p09-evidence-rag objective checks
```

## Complete these TODOs

1. `token_overlap`
2. `eligible_source_ids`
3. `retrieve`
4. `validate_grounded_output`
5. `validate_run`

## Required run record

Your `rag-run.json` must record:

- corpus snapshot ID;
- chunker/retriever/prompt/generator/evaluator versions;
- a source catalog with tenant and active-version metadata;
- fixed evaluation cases;
- relevant, retrieved, and actually supplied source IDs per case;
- structured grounded outputs;
- recall@2, grounded-answer accuracy, and unauthorized-exposure count;
- predeclared release thresholds and release decision;
- one failure → evidence → hypothesis → focused fix → result trace;
- limitations.

## Core invariants

**Authorization before ranking**

A source from another tenant or an inactive version must not enter the eligible retrieval set.

**Provenance after generation**

If `supported=true`, the output must cite a source that was actually supplied to that request.

If `supported=false`, the reduced contract uses:

```json
{"answer": null, "supported": false, "source_id": null}
```

**Stage-separated evaluation**

Retrieval success and grounded-answer success are recorded separately. A fluent final answer cannot hide a retrieval miss.

## Optional live path

You may connect a real embedding model, vector database, reranker, or generator. If you do:

- do not commit credentials;
- record exact model/index revisions;
- keep authorization filters outside prompt text;
- preserve source IDs through retrieval and prompt construction;
- record retrieval rankings and grounded outputs;
- keep the deterministic reduced path runnable.

## Project report

Add `PROJECT_REPORT.md` explaining:

- source/chunk/index lineage;
- retrieval and reranking strategy;
- tenant/access boundary;
- grounded prompt/output contract;
- citation validation;
- retrieval and answer metrics;
- one failure trace from the earliest broken boundary;
- freshness/update limitations;
- next experiment.

The project is complete when another person can reproduce why each supplied source was eligible, why each supported answer cites supplied evidence, and how the release decision was computed.

## Compare with a reference (optional)

Try the TODOs yourself and run the submission validator first. Then inspect the [published reference solution](../../reference/l09/reference_solution.py) and any example evaluations. To verify the published reference against its acceptance tests from the public materials repository root, run:

```bash
python projects/tests/l09/test_reference.py
```

This command tests the reference, **not your own solution**. Use the project rubric and submission checker to evaluate your implementation.
