"""Starter for p00-data-detective.

Complete the TODO functions without looking at the reference solution.
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
    (3, True),  # intentional failure/debug case
    (4, True),
    (7, True),
]


def predict(value, threshold):
    """Return the predicted Boolean label for one feature value."""
    # TODO: implement a threshold prediction.
    return False


def count_mistakes(rows, threshold):
    """Count prediction/label mismatches for rows of (feature, label)."""
    # TODO: compare every prediction with its label.
    return len(rows)


def choose_best_threshold(rows):
    """Choose a deterministic threshold using only the supplied training rows."""
    # TODO: evaluate candidate thresholds from the training feature values.
    return 0


def majority_label(rows):
    """Return the majority Boolean label, breaking ties toward False."""
    positives = sum(label for _, label in rows)
    return positives > len(rows) / 2


def baseline_mistakes(rows, training_rows=TRAIN_EXAMPLES):
    """Evaluate a majority-label baseline learned from training labels."""
    baseline = majority_label(training_rows)
    return sum(baseline != label for _, label in rows)


def build_report():
    """Return the clean held-out evaluation report."""
    # TODO: choose a threshold from TRAIN_EXAMPLES and evaluate TEST_EXAMPLES.
    return {
        "threshold": None,
        "model_mistakes": None,
        "baseline_mistakes": None,
        "conclusion": "TODO",
    }


if __name__ == "__main__":
    print(build_report())
