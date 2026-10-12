"""Reference implementation for p00-data-detective.

Compare only after attempting the starter TODOs; this implementation is public.
"""

TRAIN_EXAMPLES = [
    (1, False),
    (2, False),
    (4, True),
    (5, True),
    (6, True),
]

TEST_EXAMPLES = [
    (2, False),
    (3, False),
    (4, True),
    (7, True),
]

NOISY_TEST_EXAMPLES = [
    (2, False),
    (3, True),
    (4, True),
    (7, True),
]


def predict(value, threshold):
    return value >= threshold


def count_mistakes(rows, threshold):
    return sum(predict(value, threshold) != label for value, label in rows)


def choose_best_threshold(rows):
    candidates = sorted({value for value, _ in rows})
    return min(candidates, key=lambda threshold: (count_mistakes(rows, threshold), threshold))


def majority_label(rows):
    positives = sum(label for _, label in rows)
    return positives > len(rows) / 2


def baseline_mistakes(rows, training_rows=TRAIN_EXAMPLES):
    baseline = majority_label(training_rows)
    return sum(baseline != label for _, label in rows)


def build_report():
    threshold = choose_best_threshold(TRAIN_EXAMPLES)
    model_mistakes = count_mistakes(TEST_EXAMPLES, threshold)
    baseline = baseline_mistakes(TEST_EXAMPLES)
    return {
        "threshold": threshold,
        "model_mistakes": model_mistakes,
        "baseline_mistakes": baseline,
        "conclusion": "On this held-out set, the threshold predictor makes fewer mistakes than the training-majority baseline; this small test does not prove it will win on every future case.",
    }


if __name__ == "__main__":
    print(build_report())
    threshold = choose_best_threshold(TRAIN_EXAMPLES)
    print("intentional noisy-case mistakes:", count_mistakes(NOISY_TEST_EXAMPLES, threshold))
