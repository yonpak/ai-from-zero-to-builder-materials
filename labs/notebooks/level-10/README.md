# Level 10 local Labs

These Labs use Python 3.11+ and the standard library only. They are deterministic teaching exercises: no API key, live model, image service, microphone, network connection, or external package is required.

Run each command from the repository root, for example:

```bash
python labs/notebooks/level-10/l10-01-tool-boundaries.py
```

The numbered Lesson beside each Lab explains the exact field or policy value to change and what output to inspect.

The Labs intentionally separate model-like **proposals/observations** from application-owned **validation, permissions, workflow state, retry rules, and execution decisions**. L10.9 uses deterministic synthetic shared-embedding vectors plus recorded visual observations, while L10.10–L10.11 use recorded multimodal observations. None of these fixtures pretends to be a live vision or speech model.

