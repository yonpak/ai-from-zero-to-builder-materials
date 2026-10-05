from datetime import datetime, timezone

def approval_valid(proposal, approval, now):
    if not approval.get("approved"):
        return False
    if approval.get("action") != proposal.get("action"):
        return False
    if approval.get("arguments") != proposal.get("arguments"):
        return False
    expires = datetime.fromisoformat(approval["expires_at"].replace("Z", "+00:00"))
    return now < expires

now = datetime(2026, 9, 23, 18, 0, tzinfo=timezone.utc)
proposal = {"action": "refund_order", "arguments": {"order_id": "4172", "amount": 20}}
cases = {
    "approved": {"approved": True, "action": "refund_order", "arguments": {"order_id": "4172", "amount": 20}, "expires_at": "2026-09-23T19:00:00Z"},
    "mismatch": {"approved": True, "action": "refund_order", "arguments": {"order_id": "4172", "amount": 10}, "expires_at": "2026-09-23T19:00:00Z"},
    "expired": {"approved": True, "action": "refund_order", "arguments": {"order_id": "4172", "amount": 20}, "expires_at": "2026-09-23T17:00:00Z"},
    "denied": {"approved": False, "action": "refund_order", "arguments": {"order_id": "4172", "amount": 20}, "expires_at": "2026-09-23T19:00:00Z"},
}
for name, approval in cases.items():
    print(name, "=>", approval_valid(proposal, approval, now))
