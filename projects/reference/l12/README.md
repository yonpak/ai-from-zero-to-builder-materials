# Level 12 Reference

reference_solution.py is the known-good deterministic implementation for p12-agent-harness.

sample-run/harness-run.json passes the objective validator and Level 12 integration checker.

failure-run/harness-run.json intentionally contains:
- an unauthorized refund under the reader role;
- a repeated side effect using the same operation identity without reconciliation;
- a high-latency run;
- total cost above the release budget.

The submitted metrics in both fixtures are recomputed from the raw traces. The failure fixture is expected to be rejected because its release rules do not pass.
