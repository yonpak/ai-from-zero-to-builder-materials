#!/usr/bin/env python3
capacity_tokens=12000
requests=[
 {"id":"a","cached_tokens":3000},
 {"id":"b","cached_tokens":4500},
 {"id":"c","cached_tokens":6000},
]
used=0; admitted=[]; queued=[]; decisions=[]
for r in requests:
    used_before=used
    fits=used+r["cached_tokens"]<=capacity_tokens
    if fits:
        admitted.append(r["id"]); used+=r["cached_tokens"]
    else:
        queued.append(r["id"])
    decisions.append({
        "id":r["id"],
        "cached_tokens":r["cached_tokens"],
        "used_before":used_before,
        "admitted":fits,
    })

print({"admitted":admitted,"queued":queued,"used_tokens":used,"free_tokens":capacity_tokens-used})

request_ids=[r["id"] for r in requests]
assert len(admitted)+len(queued)==len(requests)
assert set(admitted).isdisjoint(queued)
assert set(admitted)|set(queued)==set(request_ids)
assert used==sum(r["cached_tokens"] for r in requests if r["id"] in admitted)
assert used<=capacity_tokens
for decision in decisions:
    should_fit=decision["used_before"]+decision["cached_tokens"]<=capacity_tokens
    assert decision["admitted"] is should_fit

if any(r["cached_tokens"]<=capacity_tokens for r in requests):
    assert admitted

print("PASS: KV-cache admission classifies every request and never exceeds the active-token budget")
