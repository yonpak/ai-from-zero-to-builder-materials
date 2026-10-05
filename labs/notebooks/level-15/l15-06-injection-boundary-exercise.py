#!/usr/bin/env python3
"""Learner exercise for L15.06: keep untrusted instructions outside authority."""


def decide(source, requested_action, trusted_allowed_actions):
    # TODO 1: classify trusted_policy as trusted and other sources as untrusted.
    # TODO 2: decide authority only from trusted_allowed_actions.
    # TODO 3: return the trust label, requested action, and allowed boolean.
    raise NotImplementedError("TODO: implement the injection boundary")


blocked = decide("retrieved_page", "read_private_records", {"public_search"})
allowed = decide("trusted_policy", "public_search", {"public_search"})
assert blocked["source_trust"] == "untrusted" and blocked["allowed"] is False
assert allowed["source_trust"] == "trusted" and allowed["allowed"] is True
print("PASS: learner boundary separates untrusted instructions from trusted authority")
