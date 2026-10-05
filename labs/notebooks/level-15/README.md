# Level 15 Labs

Level 15 uses deterministic Python exercises to practice evaluation, safety, security, governance, red teaming, frontier evidence review, and capstone release validation.

- L15.01–L15.08 use the local Python environment.
- L15.09–L15.13 target the Docker environment.

For each Docker-targeted Lab, use two steps:

1. run the deterministic Python preflight locally;
2. when Docker is available, run the same script in an actual `python:3.11-slim` container.

Example:

```bash
python3 labs/notebooks/level-15/l15-09-red-team.py
bash labs/notebooks/run-docker-preflight.sh labs/notebooks/level-15/l15-09-red-team.py
```

The required acceptance path remains standard-library Python so it needs no live model, API key, network service, GPU, cloud account, or external package. The Docker path exists to practice the real container boundary instead of treating `runtime: docker` as a label only.

Run the complete Level smoke suite:

```bash
python3 labs/notebooks/level-15/test_labs.py
```

Expected final marker:

```text
PASS: Level 15 local Lab smoke checks
```
