#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {
    "run_id", "seed", "config", "tokenizer_fingerprint",
    "checkpoint_fingerprint", "validation_loss", "samples", "environment",
}


def resolve_run_json(target: Path) -> Path:
    """Accept either a run directory or the run.json file itself."""
    return target / "run.json" if target.is_dir() else target


def validate(target: Path, drop: str | None = None) -> None:
    path = resolve_run_json(target)
    if not path.is_file():
        raise SystemExit(f"missing run metadata: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if drop is not None:
        data.pop(drop, None)
        print(f"(simulation) removed field: {drop}")

    missing = sorted(REQUIRED - data.keys())
    if missing:
        raise SystemExit("missing required field(s): " + ", ".join(missing))
    if not isinstance(data["samples"], list) or len(data["samples"]) < 2:
        raise SystemExit("samples must contain at least two fixed evaluation samples")
    if not isinstance(data["validation_loss"], (int, float)) or data["validation_loss"] <= 0:
        raise SystemExit("validation_loss must be a positive number")
    if not isinstance(data["seed"], int):
        raise SystemExit("seed must be an integer")

    print(f"PASS: packaged run {data['run_id']} has required reproducibility evidence")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path, help="run directory or path to run.json")
    parser.add_argument("--drop", choices=sorted(REQUIRED), help="simulate a missing metadata field")
    args = parser.parse_args()
    validate(args.run, args.drop)


if __name__ == "__main__":
    main()
