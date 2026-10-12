#!/usr/bin/env python3
"""Verify advanced learner exercises are intentionally incomplete and have working reference answers."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ANSWERS_ROOT = REPO / "labs" / "answers" / "advanced"
STARTERS_ROOT = REPO / "labs" / "notebooks"


def run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )


def check_level(level: int) -> None:
    answer_dir = ANSWERS_ROOT / f"level-{level}"
    starter_dir = STARTERS_ROOT / f"level-{level}"
    answers = sorted(answer_dir.glob("*-answer.py"))
    if len(answers) != 3:
        raise SystemExit(f"L{level}: expected 3 reference answers, found {len(answers)}")

    for answer in answers:
        stem = answer.name.removesuffix("-answer.py")
        starter = starter_dir / f"{stem}-exercise.py"
        if not starter.is_file():
            raise SystemExit(f"L{level}: missing learner starter for {answer.name}")

        starter_source = starter.read_text(encoding="utf-8")
        answer_source = answer.read_text(encoding="utf-8")
        compile(starter_source, str(starter), "exec")
        compile(answer_source, str(answer), "exec")

        if "TODO" not in starter_source or "NotImplementedError" not in starter_source:
            raise SystemExit(f"L{level}: starter must retain explicit TODO/NotImplementedError boundary: {starter.name}")
        if "TODO" in answer_source or "NotImplementedError" in answer_source:
            raise SystemExit(f"L{level}: reference answer still contains learner placeholder text: {answer.name}")

        starter_run = run(starter)
        starter_output = starter_run.stdout + starter_run.stderr
        if starter_run.returncode == 0:
            raise SystemExit(f"L{level}: incomplete starter unexpectedly passed: {starter.name}")
        if "NotImplementedError: TODO:" not in starter_output:
            raise SystemExit(
                f"L{level}: starter failed for the wrong reason: {starter.name}\n"
                f"STDOUT:\n{starter_run.stdout}\nSTDERR:\n{starter_run.stderr}"
            )
        if "PASS:" in starter_run.stdout:
            raise SystemExit(f"L{level}: incomplete starter emitted a PASS marker: {starter.name}")

        answer_run = run(answer)
        if answer_run.returncode != 0:
            raise SystemExit(
                f"L{level}: reference answer failed: {answer.name}\n"
                f"STDOUT:\n{answer_run.stdout}\nSTDERR:\n{answer_run.stderr}"
            )
        if "PASS:" not in answer_run.stdout:
            raise SystemExit(f"L{level}: reference answer did not emit PASS marker: {answer.name}")

        print(f"PASS: {starter.name} fails at TODO; {answer.name} satisfies contract tests")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, choices=range(10, 16), required=True)
    args = parser.parse_args()
    check_level(args.level)
    print(f"PASS: Level {args.level} learner exercise solvability checks")


if __name__ == "__main__":
    main()
