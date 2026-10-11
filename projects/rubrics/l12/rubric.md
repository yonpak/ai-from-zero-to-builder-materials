# p12-agent-harness rubric

Total: 100 points.

- **Durable task state and recovery — 20:** claims, leases, resume semantics, and task identity are explicit.
- **Replay-safe side effects — 20:** stable operation identity, retry classification, reconciliation, and duplicate detection work from raw evidence.
- **Permissions and isolation — 15:** authorization and sandbox checks remain independent and least-privilege.
- **Memory, parallelism, delegation — 15:** retrieval is bounded, dependency waves are valid, and child capabilities/budgets cannot exceed parent bounds.
- **Observability and operational metrics — 15:** traces expose enough structured evidence to recompute latency, recovery, cost, and terminal behavior.
- **Evaluation and release discipline — 15:** deterministic fixtures include negative cases; critical violations cannot be averaged away by task success.

A submission cannot receive full credit if it trusts fixture booleans for authorization, duplicate safety, or release status instead of recomputing those values from primary evidence.

## Self-check before you call it done

- Can you reproduce claimed task/lease/resume state and explain how a restarted worker identifies the same task?
- Can you derive replay-safe side effects, duplicate detection, and reconciliation from raw operation records?
- Can you show independent authorization/isolation checks and bounded memory, delegation, and parallelism?
- Can you recompute recovery/latency/cost/release evidence, including a negative fixture, without trusting summary booleans?
