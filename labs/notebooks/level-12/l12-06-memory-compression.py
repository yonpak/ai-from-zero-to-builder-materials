#!/usr/bin/env python3

items = [
    {"id": "a", "scope": "u7", "source": "verified_tool", "age": 1, "relevance": 0.9},
    {"id": "b", "scope": "u7", "source": "model_summary", "age": 1, "relevance": 0.99},
    {"id": "c", "scope": "u7", "source": "profile", "age": 4, "relevance": 0.8},
    {"id": "d", "scope": "u8", "source": "verified_tool", "age": 0, "relevance": 1.0},
]
trusted = {"verified_tool", "profile"}
max_items=3

eligible = [
    item
    for item in items
    if item["scope"] == "u7"
    and item["source"] in trusted
    and item["age"] <= 30
]
selected = sorted(
    eligible,
    key=lambda item: (-item["relevance"], item["age"]),
)[:max_items]

eligible_ids = [item["id"] for item in eligible]
selected_ids = [item["id"] for item in selected]
print("eligible:", eligible_ids)
print("selected:", selected_ids)

assert max_items >= 1
assert len(selected) <= max_items
assert all(item in eligible for item in selected)
print("PASS: retrieval respects scope, provenance, freshness, and bounds")
