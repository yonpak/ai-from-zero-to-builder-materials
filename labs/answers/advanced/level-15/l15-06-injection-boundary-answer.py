#!/usr/bin/env python3
"""Reference answer for L15.06."""


def decide(source, requested_action, trusted_allowed_actions):
    source_trust = "trusted" if source == "trusted_policy" else "untrusted"
    allowed = requested_action in trusted_allowed_actions
    return {
        "source_trust": source_trust,
        "requested_action": requested_action,
        "allowed": allowed,
    }


blocked = decide("retrieved_page", "read_private_records", {"public_search"})
assert blocked == {
    "source_trust": "untrusted",
    "requested_action": "read_private_records",
    "allowed": False,
}
trusted_but_forbidden = decide("trusted_policy", "read_private_records", {"public_search"})
assert trusted_but_forbidden["source_trust"] == "trusted"
assert trusted_but_forbidden["allowed"] is False
untrusted_but_policy_allowed = decide("retrieved_page", "public_search", {"public_search"})
assert untrusted_but_policy_allowed["source_trust"] == "untrusted"
assert untrusted_but_policy_allowed["allowed"] is True
print("PASS: L15.06 reference answer separates source trust from application-owned authority")
