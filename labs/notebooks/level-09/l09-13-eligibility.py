#!/usr/bin/env python3
"""Apply freshness and access eligibility before ranking."""

from __future__ import annotations

import argparse

BASE_SOURCES = {
    "policy-v4": {"tenant": "red", "current": True},
    "pricing-blue": {"tenant": "blue", "current": True},
    "faq-public": {"tenant": "public", "current": True},
    "policy-v3": {"tenant": "red", "current": False},
}
INDEX_ENTRIES = ["policy-v4", "pricing-blue", "faq-public", "policy-v3"]


def eligible_sources(sources: dict, tenant: str) -> list[str]:
    allowed = []
    for source_id in INDEX_ENTRIES:
        source = sources.get(source_id)
        if source is None or not source["current"]:
            continue
        if source["tenant"] in {"public", tenant}:
            allowed.append(source_id)
    return allowed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-claims-tenant", choices=["red", "blue"])
    parser.add_argument("--session-tenant", choices=["red", "blue"], default="red")
    parser.add_argument("--delete-source", choices=list(BASE_SOURCES))
    args = parser.parse_args()

    sources = {key: dict(value) for key, value in BASE_SOURCES.items()}
    if args.delete_source:
        sources.pop(args.delete_source, None)

    if args.user_claims_tenant:
        print("user-supplied tenant claim (not trusted):", args.user_claims_tenant)
    print("trusted session tenant:", args.session_tenant)

    stale = [source_id for source_id in INDEX_ENTRIES if source_id not in sources]
    print("eligible before ranking:", eligible_sources(sources, args.session_tenant))
    print("stale index entries:", stale)

    if stale:
        print("REJECT: index still contains deleted source")
        raise SystemExit(1)

    print("PASS: only current, authorized evidence is eligible before ranking")


if __name__ == "__main__":
    main()
