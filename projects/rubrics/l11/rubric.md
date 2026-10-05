# p11-bounded-agent Rubric — Bounded Agent

Score each criterion from **0–4**. A submission should score at least **16/20** and must not score 0 on authority/boundedness or evaluation.

| Criterion | 4 — Strong evidence | 3 — Meets | 2 — Partial | 1 — Weak | 0 — Missing |
|---|---|---|---|---|---|
| Goal, planning, and action choice | Goal stays explicit; subgoals are observable/revisable; selected actions match current need, available evidence, and least-authority constraints | Correct goal/subgoal/action flow with minor gaps | Functional flow but planning or action rationale is weak | Frequent irrelevant/drifting actions | No coherent goal-directed loop |
| State and memory | Working state is typed/selective with provenance; control fields are protected; persistent writes and retrieval follow scope/freshness/privacy policy | Correct state/memory boundaries with minor gaps | State works but provenance or memory policy is shallow | Mostly transcript-driven or stale memory handling | No reliable state/memory boundary |
| Authority, approval, and boundedness | Permissions are external to model output; approvals bind exact actions and expire; stop rules cover success/blocker/denial/repetition/budget with zero unsafe continuation | Correct boundaries with minor gaps | Most controls exist but one important edge is weak | Prompt wording carries major control responsibility | Unauthorized action, approval bypass, or unbounded loop can pass |
| Failure analysis and evaluation | Fixed trajectories cover key failure classes; earliest-boundary diagnosis is explicit; metrics separate task, selection, safety, memory, drift, and efficiency; release is recomputed | Strong evaluation with small omissions | Fixed cases exist but slices/diagnosis or recomputation is limited | Mostly anecdotal demos or final-answer-only checks | No meaningful trajectory evaluation |
| Reproducibility and communication | Standard-library deterministic path, versioned policy/evaluator/fixtures, exact commands, debug record, limitations, and optional live-path differences are clear | Reproducible with minor omissions | Several identities or limitations missing | Manual screenshots/output only | No reproducible package |

## Objective checks

The validator checks active/pending subgoal choice, permission-filtered action selection, protected working-memory updates, memory-write policy, exact/expiring approval binding, stopping rules, explicit transitions, raw-trajectory metric recomputation, goal-drift detection, repeated-action bounds, prohibited memory-write rejection, unauthorized execution rejection, and release-rule recomputation.

The intentional failure fixture keeps the task outcomes correct while inserting control failures. A passing implementation must reject it; final-answer success cannot compensate for authority, memory, or boundedness violations.
