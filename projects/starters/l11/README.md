# p11-bounded-agent — Bounded Agent

Build a small agent controller whose loop is explicit, bounded, reviewable, and testable.

The required project path is provider-neutral and uses only the Python standard library plus recorded JSON fixtures. You may add a live model later, but the deterministic baseline must remain runnable.

## Prerequisites

Complete Level 11 through **Bounded Agent Integration Workshop** and the Level 10 **Multimodal Tool-Using Assistant** project. You should already understand tool schemas, permissions, exact approval binding, explicit state transitions, retries, and recorded trace evaluation.

## Setup

From the repository root:

```bash
python --version
python projects/tests/l11/validate_submission.py \
  projects/starters/l11/agent.py \
  projects/tests/l11/fixtures/passing/agent-run.json
```

The starter initially fails because its TODO functions are not implemented. That failure is expected.

A Python 3.11+ environment is sufficient for the required path. No package install, API key, GPU, or network connection is required.

## Implement these functions

Open `projects/starters/l11/agent.py` and complete:

1. `choose_subgoal`
2. `select_action`
3. `update_working_memory`
4. `memory_write_allowed`
5. `approval_valid`
6. `stop_reason`
7. `transition`
8. `validate_run`

## Required behavior

Your controller must demonstrate:

- explicit active/pending/completed/blocked subgoals;
- tool/action selection from the current subgoal and permission-filtered capabilities;
- trusted working-state updates with a bounded recent-event window;
- persistent-memory policy for category, provenance, sensitivity, and freshness;
- exact, expiring human approval for approval-required side effects;
- success, denial, blocker, repetition, and maximum-step stopping;
- explicit legal state transitions;
- trajectory-wide evaluation that recomputes metrics from raw steps;
- zero-tolerance release constraints for unauthorized execution, approval bypass, runaway loops, memory-policy violations, and goal drift.

## Required recorded run

Your `agent-run.json` should include:

- project, agent, policy, memory-policy, and evaluator versions;
- `max_steps` and `repeat_limit`;
- policy and transition tables;
- at least five fixed trajectories;
- per-step subgoal, proposed action, expected action, arguments, approval, execution, and evidence-gain fields;
- memory-write candidates and whether they executed;
- expected and observed terminal state/outcome;
- recomputed metrics and release thresholds;
- one debug record and explicit limitations.

A blocked or safely denied case can count as a successful evaluation case when the expected terminal behavior is to block or deny rather than perform an unsafe action.

## Validate

Run:

```bash
python projects/tests/l11/validate_submission.py \
  projects/starters/l11/agent.py \
  projects/tests/l11/fixtures/passing/agent-run.json
```

When your implementation satisfies the objective checks, the final line is:

```text
PASS: p11-bounded-agent objective checks
```

## Project report

Add `PROJECT_REPORT.md` to your submission and explain:

- how the controller decides the active subgoal;
- why your action-selection rule prefers the chosen capability;
- which fields belong in working state versus audit history;
- which long-term memory writes are allowed or rejected and why;
- how approval is bound to an exact action;
- stop-rule priority and repeated-action handling;
- one earliest-boundary failure → hypothesis → focused fix → result trace;
- metric thresholds, zero-tolerance constraints, and remaining limitations.

## Optional live model path

You may replace fixture action proposals with a real model as extra evidence. Keep the same controller boundaries and deterministic validator. Do not commit credentials. Record the exact model/provider version and date if you add a live path.
