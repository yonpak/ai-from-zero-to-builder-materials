#!/usr/bin/env python3
"""Manual release smoke for the optional real-model and MCP integrations.

Run this only after installing labs/real-model/requirements.txt in a clean environment.
It intentionally downloads/loads a real model for the Level 10 and 11 checks.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REAL_MODEL = ROOT / "labs" / "real-model"


def run(label: str, args: list[str], required_markers: tuple[str, ...], timeout: int) -> None:
    print(f"\n=== {label} ===")
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        raise SystemExit(
            f"{label} failed with exit code {result.returncode}\n"
            f"STDERR:\n{result.stderr}"
        )
    for marker in required_markers:
        if marker not in result.stdout:
            raise SystemExit(f"{label} did not emit expected marker: {marker!r}")
    print(f"PASS: {label}")


def report_versions() -> None:
    print("=== dependency versions ===")
    for package in ("torch", "transformers", "peft", "sentence-transformers", "mcp"):
        try:
            installed = version(package)
        except PackageNotFoundError as error:
            raise SystemExit(f"missing optional dependency: {package}") from error
        print(f"{package}: {installed}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--timeout", type=int, default=900, help="per-script timeout in seconds")
    args = parser.parse_args()

    report_versions()

    run(
        "Level 13 official MCP server/client",
        [str(REAL_MODEL / "l13_mcp_client.py")],
        ("discovered_tools:", "structured_result:"),
        args.timeout,
    )
    run(
        "Level 10 real-model tool calling",
        [str(REAL_MODEL / "l10_tool_calling_real_model.py"), "--model", args.model],
        ("model_proposal:", "validated_execution:"),
        args.timeout,
    )
    run(
        "Level 11 bounded real-model agent loop",
        [str(REAL_MODEL / "l11_agent_loop_real_model.py"), "--model", args.model, "--max-steps", "3"],
        ("model_output:", "controller_execution:", "terminal_reason: final_answer"),
        args.timeout,
    )
    print("\nPASS: optional Level 10/11/13 real integration smoke")


if __name__ == "__main__":
    main()
