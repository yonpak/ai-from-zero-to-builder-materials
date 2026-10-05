# Level 11 local Labs

These Labs use only the Python standard library. They are deterministic demonstrations of the Level 11 agent-control concepts and do not require an API key or network access.

Run an individual Lab from the repository root, for example:

```bash
python labs/notebooks/level-11/l11-03-agent-loop.py
```

Run the Level smoke check:

```bash
python labs/notebooks/level-11/test_labs.py
```

The smoke check runs Labs 01–12, validates the passing Level 11 integration fixture, and confirms that the intentional failure fixture is rejected.

Expected final marker:

```text
PASS: Level 11 local Lab smoke checks
```

The Lab files are intentionally small. The Level Project under `projects/starters/l11` is where you implement the reusable bounded-agent functions and full recorded run validator.
