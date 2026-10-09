# Level 13 Labs

Level 13 practices interoperability against version-pinned protocol boundaries while keeping the required acceptance path deterministic.

- L13.1–L13.8 use deterministic local Python fixtures.
- L13.9–L13.12 target the Stage D Docker environment. Run them locally for logic-first debugging, then use the shared Docker runner when you want the real container boundary.
- MCP fixtures are pinned to `2026-07-28`.
- A2A fixtures are pinned to `1.0.0`.
- Required fixtures exercise compatibility, local authorization, task/artifact provenance, coordination, shared-state conflicts, and system evaluation. They do not define an alternate wire protocol.
- L13.4 also has an optional official-SDK MCP server/client extension under `labs/real-model/`.

Example Stage D container run:

```bash
python labs/notebooks/level-13/l13-09-coordination.py
bash labs/notebooks/run-docker-preflight.sh labs/notebooks/level-13/l13-09-coordination.py
```

