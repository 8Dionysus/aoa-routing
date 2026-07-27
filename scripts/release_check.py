#!/usr/bin/env python3
"""Run the post-G5 maintenance-only predecessor validation gate."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (
    (
        "validate maintenance-only posture",
        [
            sys.executable,
            "mechanics/release-support/parts/release-gate-routing/"
            "scripts/validate_routing_maintenance_only.py",
        ],
    ),
    (
        "validate source-home topology",
        [sys.executable, "scripts/validate_source_home.py"],
    ),
    (
        "validate mechanics topology",
        [sys.executable, "scripts/validate_mechanics_topology.py"],
    ),
    (
        "validate active legacy names",
        [sys.executable, "scripts/validate_active_legacy_names.py"],
    ),
    (
        "check decision indexes",
        [sys.executable, "scripts/generate_decision_indexes.py", "--check"],
    ),
    (
        "validate decision records",
        [sys.executable, "scripts/validate_decision_records.py"],
    ),
    (
        "run local maintenance tests",
        [sys.executable, "-m", "pytest", "-q", "tests"],
    ),
)


def run_step(label: str, command: list[str]) -> int:
    print(f"[run] {label}: {subprocess.list2cmdline(command)}", flush=True)
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=os.environ.copy(),
        check=False,
    )
    if completed.returncode != 0:
        print(
            f"[error] {label} failed with exit code {completed.returncode}",
            flush=True,
        )
        return completed.returncode
    print(f"[ok] {label}", flush=True)
    return 0


def main() -> int:
    for label, command in COMMANDS:
        exit_code = run_step(label, command)
        if exit_code != 0:
            return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
