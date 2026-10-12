#!/usr/bin/env python3
"""Reference answer for L14.03."""


def make_batches(arrivals, max_batch=3, wait_deadline=10):
    batches = []
    index = 0
    while index < len(arrivals):
        start = arrivals[index]
        batch = [arrivals[index]]
        index += 1
        while (
            index < len(arrivals)
            and len(batch) < max_batch
            and arrivals[index] - start <= wait_deadline
        ):
            batch.append(arrivals[index])
            index += 1
        batches.append(batch)
    return batches


assert make_batches([0, 3, 7, 22, 24]) == [[0, 3, 7], [22, 24]]
assert make_batches([0, 1, 2, 3], max_batch=2, wait_deadline=10) == [[0, 1], [2, 3]]
assert make_batches([0, 11], max_batch=3, wait_deadline=10) == [[0], [11]]
assert make_batches([]) == []
print("PASS: L14.03 reference answer enforces batch-size and wait-deadline bounds")
