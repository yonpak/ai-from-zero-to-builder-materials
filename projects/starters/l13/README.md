# Interoperable Agent System

Build a version-aware interoperability layer around the durable agent harness from Level 12.

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
