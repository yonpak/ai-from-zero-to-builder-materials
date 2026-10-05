#!/usr/bin/env python3
"""Learner exercise for L14.03: form bounded dynamic batches."""

ARRIVALS = [0, 3, 7, 22, 24]


def make_batches(arrivals, max_batch=3, wait_deadline=10):
    # TODO 1: start a batch at the next unassigned arrival.
    # TODO 2: add later arrivals only while size and wait-deadline bounds hold.
    # TODO 3: return batches in arrival order.
    raise NotImplementedError("TODO: implement bounded batching")


assert make_batches(ARRIVALS) == [[0, 3, 7], [22, 24]]
assert make_batches([0, 20], max_batch=3, wait_deadline=10) == [[0], [20]]
print("PASS: learner batcher respects size and wait deadlines")
