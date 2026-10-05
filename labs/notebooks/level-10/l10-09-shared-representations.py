#!/usr/bin/env python3
from math import sqrt

MOVE_TRIANGLE_TOWARD_BADGE = 0.0
CURRENT_PRINCIPAL = "user-17"

captions = {
    "a striped triangle": (0.96, 0.22),
    "a round badge": (0.18, 0.98),
    "a square tile": (-0.72, 0.54),
}

principal_records = {
    "user-17": {"roles": {"viewer"}},
    "admin-02": {"roles": {"viewer", "administrator"}},
}


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    a_norm = sqrt(sum(x * x for x in a))
    b_norm = sqrt(sum(y * y for y in b))
    return dot / (a_norm * b_norm)


def moved_triangle_representation(amount):
    if not 0.0 <= amount <= 1.0:
        raise ValueError("MOVE_TRIANGLE_TOWARD_BADGE must stay between 0.0 and 1.0")
    return (
        0.98 * (1.0 - amount) + 0.18 * amount,
        0.18 * (1.0 - amount) + 0.98 * amount,
    )


def principal_roles(principal_id):
    principal = principal_records.get(principal_id)
    return set() if principal is None else principal["roles"]


def is_authorized(principal_id, required_role):
    return required_role in principal_roles(principal_id)


triangle_image = moved_triangle_representation(MOVE_TRIANGLE_TOWARD_BADGE)
scores = {
    caption: cosine_similarity(triangle_image, vector)
    for caption, vector in captions.items()
}
ranking = sorted(scores, key=scores.get, reverse=True)

print("shared-space retrieval")
for rank, caption in enumerate(ranking, start=1):
    relation = "matched" if caption == "a striped triangle" else "mismatched"
    print(f"{rank}. {caption}: {scores[caption]:.3f} ({relation})")

badge_image = (0.82, 0.57)
authorization_text = (0.79, 0.61)
authorization_similarity = cosine_similarity(badge_image, authorization_text)
authorization_granted = is_authorized(CURRENT_PRINCIPAL, "administrator")
current_roles = principal_roles(CURRENT_PRINCIPAL)

print(
    "\nauthority boundary:",
    f"similarity={authorization_similarity:.3f}",
    f"principal={CURRENT_PRINCIPAL}",
    f"roles={sorted(current_roles)}",
    "authorization=granted" if authorization_granted else "authorization=not established",
)

assert abs(cosine_similarity((1.0, 0.0), (1.0, 0.0)) - 1.0) < 1e-12
assert authorization_similarity > 0.95
assert is_authorized("user-17", "administrator") is False
assert is_authorized("admin-02", "administrator") is True
assert principal_roles("guest-99") == set()
assert is_authorized("guest-99", "administrator") is False

if MOVE_TRIANGLE_TOWARD_BADGE == 0.0:
    assert ranking[0] == "a striped triangle"
if MOVE_TRIANGLE_TOWARD_BADGE == 1.0:
    assert ranking[0] == "a round badge"

print("\nPASS: shared representations and authorization fixture")
