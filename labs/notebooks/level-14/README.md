# Level 14 Labs

These Labs practice production-serving control without requiring a GPU, cloud account, network endpoint, or paid model provider.

- L14.1–L14.6 use deterministic local Python exercises.
- L14.7–L14.13 target the Stage D Docker environment.
- For Stage D, run the Python preflight first, then run the same script in a real container when Docker is available. Repository acceptance intentionally uses the local preflight so container setup does not hide service/controller bugs.
- The exercises model API validation, batching, memory/KV-cache admission, scheduling, deployment identity, telemetry, rollout gates, and capacity recovery.

Example:

```bash
python labs/notebooks/level-14/l14-09-deployment-identity.py
bash labs/notebooks/run-docker-preflight.sh labs/notebooks/level-14/l14-09-deployment-identity.py
```

The second command launches `python:3.11-slim` with the repository mounted into the container; the script itself remains deterministic and offline.

