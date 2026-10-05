# p07-reliable-llm-workflow — Reliable LLM Workflow

## Goal

Build and review a model-facing workflow whose reliability comes from explicit contracts rather than one lucky generated answer.

Your workflow must keep these boundaries visible:

```text
task contract
→ context selection
→ model-facing request
→ decoding configuration
→ structured output
→ schema/provenance validation
→ abstention or accepted answer
→ fixed-case evaluation
```

## Prerequisites

Complete Level 7 through **Reliable LLM Workflow Review**. The cumulative project dependency is **Train and Ship a Tiny LLM**.

## Reduced validation path

The committed acceptance path uses Python 3.11+ standard-library features only. It does **not** call an external model API, so the important workflow contracts can be tested deterministically.

Run:

```bash
python projects/tests/l07/validate_submission.py \
  projects/starters/l07/workflow.py \
  path/to/your/workflow-run.json
```

Expected success marker:

```text
PASS: p07-reliable-llm-workflow objective checks
```

## Your task

Complete the TODOs in `workflow.py`:

1. `word_overlap(query, text)`
2. `retrieve(query, documents, k=1)`
3. `validate_model_output(output, supplied_source_ids)`
4. `evaluate_cases(cases)`
5. `validate_run(data)`

Produce a `workflow-run.json` that records:

- workflow, model, and prompt identity;
- decoding/seed policy;
- source catalog;
- fixed evaluation cases;
- the exact source IDs supplied to each case;
- structured output for each case;
- supported/unsupported expectations;
- one failure/debug record;
- limitations.

## Required behavior

A supported output must have:

- non-empty `answer`;
- `supported: true`;
- a non-empty `source_id`;
- a `source_id` that was actually supplied for that case.

An unsupported output must have:

- `answer: null`;
- `supported: false`;
- `source_id: null`.

The validator deliberately rejects an answer that cites a source that was not supplied to the model-facing context.

## Optional full-model path

You may connect a real model provider and replace the reduced fixture outputs with recorded model responses. If you do:

- do not commit credentials;
- record the exact model/version when available;
- record decoding settings and retry policy;
- preserve source IDs and raw/validated output evidence;
- keep the deterministic reduced path runnable for reviewers.

## Project report

Add a short `PROJECT_REPORT.md` explaining:

- the task contract;
- context-selection strategy;
- structured-output contract;
- abstention rule;
- trust boundary for untrusted content;
- evaluation set and failure slices;
- one failure → evidence → hypothesis → focused fix → result trace;
- limitations and next test.

The project is successful when another person can explain why each accepted answer is grounded in supplied evidence and reproduce the evaluation result.
