#!/usr/bin/env python3
from __future__ import annotations
import json

def decide(source: str, requested_action: str, trusted_allowed_actions: set[str]) -> dict:
    source_trust = "trusted" if source == "trusted_policy" else "untrusted"
    allowed = requested_action in trusted_allowed_actions
    return {
        "source_trust": source_trust,
        "requested_action": requested_action,
        "allowed": allowed,
    }

if __name__ == "__main__":
    SOURCE = "retrieved_page"                # where the instruction-like text came from
    REQUESTED_ACTION = "read_private_records"  # what the text asks the agent to do
    ALLOWED_FOR_THIS_TASK = {"public_search"}   # set by the application, not by any text
    result = decide(SOURCE, REQUESTED_ACTION, ALLOWED_FOR_THIS_TASK)
    print(json.dumps(result, sort_keys=True))
