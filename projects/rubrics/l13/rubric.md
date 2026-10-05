# p13-interoperable-agent-system rubric

Total: 100 points.

- **Protocol/version discipline — 20:** MCP 2026-07-28 and A2A v1.0.0 boundaries are explicit and incompatible versions fail visibly.
- **Capability and trust mapping — 20:** discovered MCP capabilities remain subject to local role/task policy and remote data is not treated as authority.
- **A2A task/artifact provenance — 15:** agent selection uses compatible capability/interface evidence and artifacts remain bound to the expected child task.
- **Shared-state coordination — 15:** stale writes are detected with version checks and conflict handling remains explicit.
- **System evaluation — 20:** task, compatibility, authority, provenance, conflict, and coordination metrics are recomputed from raw events.
- **Reproducibility and operational clarity — 10:** deterministic local tests and the Docker bridge clearly separate protocol/controller logic from environment setup.

Full credit requires independent recomputation of critical facts. Remote or fixture booleans must not be trusted as the source of authorization, provenance, or release truth.
