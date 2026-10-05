#!/usr/bin/env python3
"""L14.4 local Lab: a GPU memory budget has four parts, and only one grows with traffic."""
TOTAL_GB = 24.0
weights_gb = 14.0
workspace_gb = 2.0
reserve_gb = 2.0
active_sequences = 8  # try 16
kv_per_sequence_gb = 0.5

parts = {
    "weights": weights_gb,
    "workspace": workspace_gb,
    "reserve": reserve_gb,
    "kv_cache": active_sequences * kv_per_sequence_gb,
}
used = sum(parts.values())
headroom = TOTAL_GB - used
print("active_sequences:", active_sequences)
print("parts_gb:", parts)
print({"used_gb": used, "headroom_gb": headroom})
if headroom < 0:
    print(f"DOES NOT FIT: over the {TOTAL_GB} GB device by {-headroom} GB; admit fewer sequences")
    raise SystemExit(1)
print("PASS: memory budget includes weights, workspace, cache, and reserve")
