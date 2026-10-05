"""Helpers for intentional-failure fixtures used by project reference tests."""

from __future__ import annotations

from contextlib import contextmanager
import subprocess
import sys
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Iterable, Iterator


@contextmanager
def mutated_copy(
    source: Path,
    replacements: tuple[str, str] | Iterable[tuple[str, str]],
    *,
    filename: str | None = None,
) -> Iterator[Path]:
    """Yield a temporary copy with exact, reviewable mutations applied."""
    if isinstance(replacements, tuple) and len(replacements) == 2 and all(
        isinstance(item, str) for item in replacements
    ):
        edits = [replacements]
    else:
        edits = list(replacements)

    text = source.read_text(encoding="utf-8")
    for old, new in edits:
        count = text.count(old)
        if count != 1:
            raise AssertionError(
                f"failure-fixture anchor must appear exactly once in {source}: {old!r}; found {count}"
            )
        text = text.replace(old, new, 1)

    with TemporaryDirectory(prefix="project-failure-fixture-") as tmp:
        target = Path(tmp) / (filename or source.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        yield target


def expect_rejected(
    args: list[object],
    description: str,
    *,
    marker: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a Python validator and require a non-zero exit for the intended fixture."""
    result = subprocess.run(
        [sys.executable, *[str(arg) for arg in args]],
        text=True,
        capture_output=True,
    )
    output = result.stdout + result.stderr
    if result.returncode == 0:
        raise AssertionError(
            f"intentional failure fixture was accepted: {description}\n{output}"
        )
    if marker is not None and marker not in output:
        raise AssertionError(
            f"fixture failed for an unexpected reason: {description}\n"
            f"expected marker: {marker!r}\n{output}"
        )
    print(f"PASS: validator rejected intentional failure fixture ({description})")
    return result
