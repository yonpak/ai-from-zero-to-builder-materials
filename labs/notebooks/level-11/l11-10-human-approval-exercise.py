#!/usr/bin/env python3
"""Learner exercise for L11.10: bind approval to one exact action."""

from datetime import datetime, timezone


def approval_valid(proposal, approval, now):
    # TODO 1: require explicit approved=True.
    # TODO 2: bind approval to the same action and exact arguments.
    # TODO 3: reject expired approvals.
    raise NotImplementedError("TODO: implement approval binding")


now = datetime(2026, 9, 23, 18, 0, tzinfo=timezone.utc)
proposal = {"action": "refund_order", "arguments": {"order_id": "4172", "amount": 20}}
approved = {"approved": True, "action": "refund_order", "arguments": {"order_id": "4172", "amount": 20}, "expires_at": "2026-09-23T19:00:00Z"}
mismatch = {**approved, "arguments": {"order_id": "4172", "amount": 10}}
expired = {**approved, "expires_at": "2026-09-23T17:00:00Z"}
assert approval_valid(proposal, approved, now)
assert not approval_valid(proposal, mismatch, now)
assert not approval_valid(proposal, expired, now)
print("PASS: learner approval gate binds scope and expiry")
