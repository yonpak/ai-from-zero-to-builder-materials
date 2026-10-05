#!/usr/bin/env python3

proposals = [
    {"id": "p1", "evidence": [], "subgoal": "refund", "active_subgoal": "refund"},
    {
        "id": "p2",
        "evidence": ["eligible"],
        "subgoal": "message",
        "active_subgoal": "refund",
    },
    {
        "id": "p3",
        "evidence": ["eligible"],
        "subgoal": "refund",
        "active_subgoal": "refund",
    },
]


def critique(proposal):
    issues = []
    if not proposal.get("evidence"):
        issues.append("missing_evidence")
    if proposal.get("subgoal") != proposal.get("active_subgoal"):
        issues.append("goal_mismatch")
    return issues


max_revisions = 1

for proposal in proposals:
    issues = critique(proposal)
    if not issues:
        action = "accept"
        issue_text = "none"
    elif max_revisions > 0:
        action = f"revise (1 of {max_revisions})"
        issue_text = repr(issues)
    else:
        action = "record issue and escalate (no revision allowed)"
        issue_text = repr(issues)

    print(f"{proposal['id']} issues: {issue_text} => {action}")
