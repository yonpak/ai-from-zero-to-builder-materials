#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def resolve_run_json(target: Path) -> Path:
    """Accept either a run directory or the run.json file itself."""
    return target / "run.json" if target.is_dir() else target


def check(target: Path) -> None:
    path = resolve_run_json(target)
    if not path.is_file():
        raise SystemExit(f"missing run metadata: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "run_id",
        "tokenizer_fingerprint",
        "checkpoint_tokenizer_fingerprint",
        "checkpoint_fingerprint",
        "validation_loss",
        "samples",
        "debug_record",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        raise SystemExit("missing integration field(s): " + ", ".join(missing))
    if data["tokenizer_fingerprint"] != data["checkpoint_tokenizer_fingerprint"]:
        raise SystemExit("tokenizer/checkpoint fingerprint mismatch")

    debug = data["debug_record"]
    for key in ["failure", "evidence", "hypothesis", "fix", "result"]:
        if not str(debug.get(key, "")).strip():
            raise SystemExit(f"debug_record missing {key}")
    if len(data["samples"]) < 2:
        raise SystemExit("need at least two fixed samples")

    print(f"PASS: integration invariants hold for {data['run_id']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path, help="run directory or path to run.json")
    args = parser.parse_args()
    check(args.run)


if __name__ == "__main__":
    main()
