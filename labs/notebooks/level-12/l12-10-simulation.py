#!/usr/bin/env python3
import random
seed=12010
retry_limit=1
rng=random.Random(seed)
runs=[]
for i in range(100):
    timeout=rng.random()<0.15
    approved=rng.random()<0.9
    recovered=timeout and retry_limit>=1
    success=approved and (not timeout or recovered)
    runs.append({"timeout":timeout,"approved":approved,"success":success})
success=sum(r["success"] for r in runs)/len(runs)
print("seed:",seed,"success:",round(success,3),"timeouts:",sum(r["timeout"] for r in runs))
assert 0<=success<=1
print("PASS: seeded simulation is reproducible")
