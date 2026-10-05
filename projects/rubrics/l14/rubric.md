# p14-production-ai-service rubric

Total: 100 points.

- **API and admission control — 20:** request bounds and resource admission are deterministic and reject unsafe work before expensive execution.
- **Batching and resource accounting — 15:** batch formation and memory reserve rules remain explicit and testable.
- **Deployment reproducibility — 15:** image, service, model, runtime, and configuration identity are preserved.
- **Observability and performance — 15:** success and latency evidence can be recomputed from raw run records.
- **Rollout and recovery — 20:** critical violations block release, deployment mismatch is visible, and capacity logic preserves operational headroom.
- **Reproducibility — 15:** offline tests and the Docker bridge separate controller correctness from GPU/cloud environment setup.

Full credit requires recomputing critical release evidence rather than trusting fixture fields such as admitted, healthy, or release_passed when primary evidence is available.
