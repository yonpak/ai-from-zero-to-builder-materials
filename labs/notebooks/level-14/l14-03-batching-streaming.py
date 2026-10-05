#!/usr/bin/env python3
"""L14.3 local Lab: a batch dispatches when it is full or when its oldest request has waited long enough."""
arrivals = [0, 3, 7, 22, 24]  # request arrival times in ms
max_batch = 3
wait_deadline = 2  # ms the oldest request may wait; try 10

batches = []
i = 0
while i < len(arrivals):
    start = arrivals[i]
    batch = [arrivals[i]]
    i += 1
    while i < len(arrivals) and len(batch) < max_batch and arrivals[i] - start <= wait_deadline:
        batch.append(arrivals[i])
        i += 1
    dispatch = batch[-1] if len(batch) == max_batch else start + wait_deadline
    batches.append((batch, dispatch))

for batch, dispatch in batches:
    print(f"batch {batch} dispatched at t={dispatch} ms, oldest request waited {dispatch - batch[0]} ms")
print("batch count:", len(batches))
print("longest queue wait:", max(d - b[0] for b, d in batches), "ms")
assert all(len(b) <= max_batch and d - b[0] <= wait_deadline for b, d in batches)
print("PASS: batching respects size and wait deadline")
