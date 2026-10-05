#!/usr/bin/env python3
"""L14.5 local Lab: pick a serving representation by support, quality, and measured throughput."""
MIN_QUALITY = 0.92
profiles = [
    {"name": "fp16", "weight_gb": 14.0, "quality": 0.94, "throughput": 80, "hardware_support": True},
    {"name": "int8", "weight_gb": 8.0, "quality": 0.93, "throughput": 105, "hardware_support": True},
    {"name": "int4", "weight_gb": 5.0, "quality": 0.88, "throughput": 95, "hardware_support": False},
]
eligible = []
for p in profiles:
    reasons = []
    if not p["hardware_support"]:
        reasons.append("no fast kernel on this hardware")
    if p["quality"] < MIN_QUALITY:
        reasons.append(f"quality {p['quality']} < {MIN_QUALITY}")
    print(f"{p['name']:5s} {p['weight_gb']:>5} GB  quality={p['quality']}  throughput={p['throughput']}  ->",
          "eligible" if not reasons else "excluded: " + "; ".join(reasons))
    if not reasons:
        eligible.append(p)
assert all(p["hardware_support"] and p["quality"] >= MIN_QUALITY for p in eligible)
assert len(eligible) == sum(
    1 for p in profiles if p["hardware_support"] and p["quality"] >= MIN_QUALITY
)

if eligible:
    best = max(eligible, key=lambda p: p["throughput"])
    assert best["throughput"] == max(p["throughput"] for p in eligible)
    print("selected:", best["name"])
else:
    best = None
    print(
        "selected: none — no profile meets both hardware support and "
        f"MIN_QUALITY={MIN_QUALITY}"
    )

print("PASS: serving representation selection handles both eligible and no-eligible outcomes explicitly")
