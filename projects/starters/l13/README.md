# Interoperable Agent System

Build a version-aware interoperability layer around the durable agent harness from Level 12.

## Prerequisites

Python help for this project:

- [P9 — Writing Reliable Python](https://aizero.ruzincompany.com/learn/10-level-10/writing-reliable-python)
- [P10 (optional real-model track) — Python for Real AI Services](https://aizero.ruzincompany.com/learn/12-level-12/python-for-real-ai-services)

## Pinned protocol versions

- MCP: `2026-07-28`
- A2A: `1.0.0`

The objective path uses deterministic fixtures. It does not require a public MCP endpoint, A2A agent, live model, network call, or secret.

## Implement

Complete the TODO functions in `system.py`:

1. protocol-version compatibility;
2. local filtering of MCP capabilities;
3. A2A agent selection by version, skill, and interface;
4. task/artifact provenance validation;
5. versioned shared-state updates;
6. raw-event evaluation and release decisions.

Run:

    python projects/tests/l13/validate_submission.py \
      projects/starters/l13/system.py \
      projects/tests/l13/fixtures/passing/system-run.json

The starter is expected to fail until the TODO functions are implemented.

## Docker bridge

Later Level 13 coordination Labs use a Docker-oriented environment. The Dockerfile provides a reproducible Python base for your own integration experiments. The required objective tests deliberately remain offline and deterministic so a protocol-logic failure can be separated from container, network, endpoint, or credential setup.

## Compare with a reference (optional)

Try the TODOs yourself and run the submission validator first. Then inspect the [published reference solution](../../reference/l13/reference_solution.py) and any example evaluations. To verify the published reference against its acceptance tests from the public materials repository root, run:

```bash
python projects/tests/l13/test_reference.py
```

This command tests the reference, **not your own solution**. Use the project rubric and submission checker to evaluate your implementation.
