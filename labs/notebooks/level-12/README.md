# Level 12 Labs

These Labs exercise agent-harness engineering without requiring a live model provider.

L12.1–L12.8 use deterministic local Python exercises for durable state, retries, tracing, permissions, memory, parallelism, and delegation.

L12.9–L12.13 target the Stage D Docker environment. Each has two deliberately separate paths:

1. **Required deterministic preflight** — run the Python script directly so logic failures are easy to debug and CI stays independent from Docker/GPU/cloud availability.
2. **Container execution** — run the same preflight inside a real Python 3.11 container with the shared Docker runner.

Example:

```bash
python labs/notebooks/level-12/l12-09-test-fixtures.py
bash labs/notebooks/run-docker-preflight.sh labs/notebooks/level-12/l12-09-test-fixtures.py
```

The Docker command actually launches the Lab in `python:3.11-slim`; it is not required by repository smoke tests.

