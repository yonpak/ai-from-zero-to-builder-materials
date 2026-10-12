# Level 13 Reference

The reference solution validates the pinned MCP 2026-07-28 and A2A v1.0.0 boundaries without contacting public services.

The passing fixture contains:
- an authorized MCP read;
- a correct A2A child artifact;
- an authorized operator side effect;
- one detected shared-state conflict inside the allowed release budget;
- one remote task waiting for input.

The intentional failure fixture adds:
- an MCP version mismatch;
- an unauthorized capability call;
- an artifact attached to the wrong child task;
- a second shared-state conflict beyond the release rule.

Critical metrics are recomputed from raw role, protocol version, event kind, capability, task identity, and state-version evidence.
