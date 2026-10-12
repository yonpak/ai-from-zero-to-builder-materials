# Level 14 Reference

The reference solution exercises production-serving control without a real accelerator.

The passing fixture has:
- five valid executed requests;
- memory estimates that preserve the configured reserve;
- exact deployment image/model/runtime identity;
- no critical violations;
- p95 time-to-first-token within the release threshold.

The intentional failure fixture adds:
- one oversized executed request;
- one memory admission beyond the safe reserve;
- one deployment image mismatch;
- one critical rollout violation;
- slower tail latency.

The validator recomputes critical metrics from raw request, resource, deployment, and timing evidence.
