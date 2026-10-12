#!/usr/bin/env python3
"""Reference answer for L11.10."""

from datetime import datetime, timezone


def approval_valid(proposal, approval, now):
    if not approval.get("approved"):
        return False
    if approval.get("action") != proposal.get("action"):
        return False
    if approval.get("arguments") != proposal.get("arguments"):
        return False
    expires_at = approval.get("expires_at")
    if not isinstance(expires_at, str):
        return False
    expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    return now < expires


now = datetime(2026, 9, 23, 18, 0, tzinfo=timezone.utc)
proposal = {"action": "refund_order", "arguments": {"order_id": "4172", "amount": 20}}
approved = {"approved": True, "action": "refund_order", "arguments": {"order_id": "4172", "amount": 20}, "expires_at": "2026-09-23T19:00:00Z"}
assert approval_valid(proposal, approved, now)
assert not approval_valid(proposal, {**approved, "approved": False}, now)
assert not approval_valid(proposal, {**approved, "action": "cancel_order"}, now)
assert not approval_valid(proposal, {**approved, "arguments": {"order_id": "4172", "amount": 10}}, now)
assert not approval_valid(proposal, {**approved, "expires_at": "2026-09-23T18:00:00Z"}, now)
print("PASS: L11.10 reference answer binds approval flag, action, arguments, and expiry")
