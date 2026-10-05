# p10-tool-using-assistant Rubric — Multimodal Tool-Using Assistant

Score each criterion from **0–4**. A submission should score at least **16/20** and must not score 0 on authority/security or evaluation.

| Criterion | 4 — Strong evidence | 3 — Meets | 2 — Partial | 1 — Weak | 0 — Missing |
|---|---|---|---|---|---|
| Tool/schema design | Narrow task-shaped tools, typed schemas, extra-field policy, result allowlists, and clear read/write separation | Complete interfaces with minor gaps | Functional tools but loose schema or result boundaries | Broad ambiguous tools | No coherent tool interface |
| Authority, approval, and state | Trusted principal, least privilege, exact approval binding, explicit legal transitions, and denied-action traces | Correct boundaries with minor gaps | Some checks but one important authority/state boundary is weak | Prompt wording carries major policy responsibility | Unauthorized execution/approval bypass can pass |
| Error/retry/result handling | Failure categories, bounded retries, side-effect idempotency handling, normalized results, and provenance are demonstrated | Complete handling with minor gaps | Retry or normalization works but edge cases are shallow | Blind retries or raw result dumping | No reliable failure/result path |
| Multimodal and workflow evaluation | Text/image/audio slices, tool-selection/task metrics, zero-tolerance security metrics, and earliest-boundary failure analysis | Strong evaluation with small omissions | Fixed cases exist but slices/diagnosis are limited | Mostly anecdotal demos | No fixed evaluation |
| Reproducibility and communication | Versioned workflow/schema/policy/evaluator, commands, fixtures, limitations, optional live-path differences, and debug record are explicit | Reproducible with minor omissions | Several identities or limitations missing | Screenshots/output only | No reproducible package |

## Objective checks

The validator checks tool selection, schema/range rejection, result allowlisting, role permissions, approval binding, retry/idempotency decisions, state transitions, input-evidence identity, text/image/audio slice metrics, run metrics, release recomputation, and intentional unsafe-fixture rejection.
