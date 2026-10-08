#!/usr/bin/env python3
import random
seed=12010
retry_limit=1
MAX_ATTEMPTS=4
rng=random.Random(seed)
# Draw every task's outcomes up front so changing retry_limit changes only how many attempts are used.
tasks=[]
for i in range(100):
    approved=rng.random()<0.9
    # Each attempt: (timed_out, side_effect_committed_before_the_timeout)
    attempts=[(rng.random()<0.35,rng.random()<0.5) for _ in range(MAX_ATTEMPTS)]
    tasks.append((approved,attempts))

successes=retries=duplicate_risk=0
for approved,attempts in tasks:
    if not approved:
        continue
    effects=0
    for number,(timed_out,committed) in enumerate(attempts[:1+retry_limit]):
        if number>0:
            retries+=1
        if not timed_out:
            effects+=1
            successes+=1
            break
        if committed:
            effects+=1
    # Without an idempotency key, a retry after a committed-but-timed-out attempt can repeat the side effect.
    if effects>1:
        duplicate_risk+=1

approved_count=sum(approved for approved,_ in tasks)
print("seed:",seed,"retry_limit:",retry_limit)
print("success:",round(successes/len(tasks),2),"retries:",retries,"duplicate_risk:",duplicate_risk)
assert 0<=successes<=approved_count
assert retries<=retry_limit*approved_count
print("PASS: seeded simulation is reproducible")
