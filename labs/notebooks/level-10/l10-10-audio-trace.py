#!/usr/bin/env python3
segments = [
    {"id": "clean", "start": 12.4, "end": 15.1, "expected": "ship fifteen units", "transcript": "ship fifteen units"},
    {"id": "noisy", "start": 12.4, "end": 15.1, "expected": "ship fifteen units", "transcript": "ship fifty units"},
]

def exact_words(segment):
    expected = segment["expected"].split()
    actual = segment["transcript"].split()
    return sum(a == b for a, b in zip(expected, actual)), len(expected)

for segment in segments:
    matched, total = exact_words(segment)
    print(segment["id"], f"{matched}/{total}", f"{segment['start']}-{segment['end']}")

assert exact_words(segments[0]) == (3, 3)
assert exact_words(segments[1]) == (2, 3)
