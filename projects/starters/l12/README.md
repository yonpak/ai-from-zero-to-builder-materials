# Production-Grade Agent Harness

This project turns the bounded agent from Level 11 into a durable, observable controller.

## What you implement

Complete the TODO functions in harness.py:

1. durable task claiming with leases;
2. deterministic operation identities for side effects;
3. retry classification and backoff;
4. role/action authorization;
5. sandbox-profile checks;
6. bounded memory retrieval;
7. dependency-respecting parallel waves;
8. bounded delegation;
9. run evaluation and release checks.

The objective tests use recorded fixtures. They do not require a live LLM, network call, cloud account, GPU, or secret.

## Local setup

Use Python 3.11 or newer.

    python projects/tests/l12/validate_submission.py \
      projects/starters/l12/harness.py \
      projects/tests/l12/fixtures/passing/harness-run.json

Your initial starter is expected to fail because the TODO functions are incomplete.

## Docker bridge

Later Level 12 activities use a Docker-oriented environment boundary. The included Dockerfile provides a reproducible Python container for the project without adding provider credentials.

Build:

    docker build -t p12-agent-harness projects/starters/l12

Run the local test command by mounting the repository when you want the container to see project fixtures. Docker setup failure is an environment problem; objective validator failures after Python starts are harness-logic problems.

## Evidence to inspect

A passing run recomputes task success, unauthorized executions, duplicate side effects, recovered failures, p95 latency, and total cost from raw traces. Do not trust a fixture's derived authorization or release flags without recomputation.
