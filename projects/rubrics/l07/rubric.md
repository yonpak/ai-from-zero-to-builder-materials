# p07-reliable-llm-workflow Rubric — Reliable LLM Workflow

Score each criterion from **0–4**. A submission should score at least **16/20** overall and must not score 0 on provenance/validation or evaluation.

| Criterion | 4 — Strong evidence | 3 — Meets | 2 — Partial | 1 — Weak | 0 — Missing |
|---|---|---|---|---|---|
| Task and prompt interface | Task, input boundary, constraints, output contract, and abstention behavior are explicit and testable | Clear interface with minor omissions | Interface exists but some requirements remain vague | Mostly prompt prose without a checkable contract | No coherent task contract |
| Context and provenance | Context-selection strategy is documented; every accepted answer cites a source supplied for that exact request; untrusted content remains visibly untrusted | Correct source/context handling with small gaps | Provenance exists but is incomplete or inconsistent | Source catalog exists without per-request grounding | No source/context evidence |
| Structured validation and trust boundaries | Parse/schema/provenance/business rules are separated; unsupported output abstains; sensitive actions are bounded outside the model | Correct validation flow with minor gaps | Some validation but important boundary missing | Trust placed mainly in prompt wording | No meaningful validation |
| Evaluation and failure analysis | Fixed diverse cases, aggregate + failed-case evidence, controlled conditions, and one failure→evidence→hypothesis→fix→result trace | Complete evaluation with minor gaps | Evaluation present but shallow or overfit | A few cherry-picked samples only | No evaluation |
| Reproducibility and communication | Prompt/model/evaluator/context/decoding identities, commands, limitations, and optional live-model differences are recorded clearly | Reproducible package with small omissions | Important identity/configuration missing | Mostly screenshots/output dump | No reproducible package |

## Exit-skill mapping

- **Design/evaluate prompts:** Task and prompt interface; evaluation.
- **Manage context:** Context and provenance.
- **Request structured outputs:** Structured validation.
- **Recognize hallucination/injection risks:** Trust boundaries; failure analysis.
- **Measure reliability:** Evaluation and reproducibility.

## Objective checks

The reduced validator checks retrieval behavior, structured-output provenance, abstention, fixed-case evaluation, run metadata, and the intentional unsupplied-source failure.

Human review scores whether the actual prompt/context choices, trust boundaries, evaluation coverage, and conclusions are technically convincing.

## Assessment guardrail

A live provider model is optional for repository acceptance. If one is used, model output does not need to match the reference text. The project rewards explicit contracts and evidence rather than provider-specific prompt tricks.
