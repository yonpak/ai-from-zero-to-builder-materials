# p10-tool-using-assistant — Multimodal Tool-Using Assistant

## Goal

Build a bounded tool workflow whose authority and evidence remain inspectable:

```text
request + trusted principal/state
→ tool selection
→ structured argument validation
→ authorization / approval
→ execution or direct response
→ normalized result
→ retry decision
→ state transition
→ final outcome
→ evaluation + release decision
```

## Setup

Python 3.11+ is sufficient. The required path uses no external package and no API key.

```bash
python projects/tests/l10/validate_submission.py \
  projects/starters/l10/assistant.py \
  path/to/your/tool-run.json
```

Expected success marker:

```text
PASS: p10-tool-using-assistant objective checks
```

## Complete these TODOs

1. `select_tool`
2. `validate_arguments`
3. `normalize_tool_result`
4. `authorize_action`
5. `next_retry_action`
6. `transition`
7. `validate_run`

## Required run record

Your `tool-run.json` must include tool/schema/policy/evaluator versions, available tool identities, fixed text/image/audio traces with input evidence identity, structured arguments, authorization and approval decisions, retry evidence, state transitions, normalized results, overall and per-modality metrics, release thresholds, one debug trace, and limitations.

Text, image, and audio success rates are recomputed separately so a strong text slice cannot hide a weak visual or audio slice. Security constraints are evaluated separately from task averages. Unauthorized executions, approval bypasses, and runaway workflows must remain at zero.

## Optional live path

You may connect a real model, API, vision model, or speech model as extra evidence. Do not commit credentials. Keep the deterministic fixture path runnable, record exact external model/API versions, and keep permissions/approvals outside prompt text.

## Project report

Add `PROJECT_REPORT.md` describing:

- tool interfaces and why they are narrow;
- schema and domain validation;
- trusted principal and permission source;
- approval binding for side effects;
- retry/idempotency policy;
- state-machine design and stop conditions;
- result normalization/provenance;
- multimodal evidence limitations;
- evaluation slices and release rule;
- one earliest-boundary failure → hypothesis → focused fix → result trace.
