#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from router_core import default_dependency_root

REPO_ROOT = Path(__file__).resolve().parents[1]

DEPENDENCIES = {
    "skills": "aoa-skills",
    "techniques": "aoa-techniques",
    "evals": "aoa-evals",
    "stats": "aoa-stats",
    "memo": "aoa-memo",
    "agents": "aoa-agents",
    "aoa": "Agents-of-Abyss",
    "playbooks": "aoa-playbooks",
    "kag": "aoa-kag",
    "tos": "Tree-of-Sophia",
    "sdk": "aoa-sdk",
    "source_route": "Dionysus",
    "profile": "8Dionysus",
    "abyss_stack": "abyss-stack",
}


def _resolve(repo_name: str) -> Path:
    override = None
    if repo_name == "abyss-stack":
        override = os.environ.get("ABYSS_STACK_ROOT") or os.environ.get("AOA_SOURCE_ROOT")
    candidates = [
        Path(override).expanduser() if override else None,
        default_dependency_root(repo_name, REPO_ROOT),
    ]
    for candidate in candidates:
        if candidate is not None and candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f"missing required sibling repo {repo_name}")


def _command_with_roots(command: str) -> list[str]:
    roots = {key: _resolve(value) for key, value in DEPENDENCIES.items()}
    if command == "validate_router":
        return [
            sys.executable,
            "scripts/validate_router.py",
            "--techniques-root",
            str(roots["techniques"]),
            "--skills-root",
            str(roots["skills"]),
            "--evals-root",
            str(roots["evals"]),
            "--stats-root",
            str(roots["stats"]),
            "--memo-root",
            str(roots["memo"]),
            "--agents-root",
            str(roots["agents"]),
            "--aoa-root",
            str(roots["aoa"]),
            "--playbooks-root",
            str(roots["playbooks"]),
            "--kag-root",
            str(roots["kag"]),
            "--tos-root",
            str(roots["tos"]),
            "--sdk-root",
            str(roots["sdk"]),
            "--source-route-root",
            str(roots["source_route"]),
            "--profile-root",
            str(roots["profile"]),
            "--abyss-stack-root",
            str(roots["abyss_stack"]),
        ]
    if command == "build_router_check":
        return [
            sys.executable,
            "scripts/build_router.py",
            "--techniques-root",
            str(roots["techniques"]),
            "--skills-root",
            str(roots["skills"]),
            "--evals-root",
            str(roots["evals"]),
            "--stats-root",
            str(roots["stats"]),
            "--memo-root",
            str(roots["memo"]),
            "--agents-root",
            str(roots["agents"]),
            "--aoa-root",
            str(roots["aoa"]),
            "--playbooks-root",
            str(roots["playbooks"]),
            "--kag-root",
            str(roots["kag"]),
            "--tos-root",
            str(roots["tos"]),
            "--sdk-root",
            str(roots["sdk"]),
            "--source-route-root",
            str(roots["source_route"]),
            "--profile-root",
            str(roots["profile"]),
            "--abyss-stack-root",
            str(roots["abyss_stack"]),
            "--check",
        ]
    if command == "two_stage_build":
        return [
            sys.executable,
            "scripts/build_two_stage_skill_router.py",
            "--routing-root",
            str(REPO_ROOT),
            "--skills-root",
            str(roots["skills"]),
            "--check",
        ]
    if command == "two_stage_validate":
        return [
            sys.executable,
            "scripts/validate_two_stage_skill_router.py",
            "--routing-root",
            str(REPO_ROOT),
            "--skills-root",
            str(roots["skills"]),
        ]
    raise ValueError(command)


COMMANDS = [
    ("validate source-home topology", [sys.executable, "scripts/validate_source_home.py"]),
    ("validate mechanics topology", [sys.executable, "scripts/validate_mechanics_topology.py"]),
    ("validate active legacy names", [sys.executable, "scripts/validate_active_legacy_names.py"]),
    ("validate routing surfaces", "validate_router"),
    ("check rebuild parity", "build_router_check"),
    (
        "validate OS Abyss routing artifact bundle",
        [sys.executable, "scripts/validate_abyss_machine_routing_bundle.py"],
    ),
    ("check decision indexes", [sys.executable, "scripts/generate_decision_indexes.py", "--check"]),
    ("validate decision records", [sys.executable, "scripts/validate_decision_records.py"]),
    ("run tests", [sys.executable, "-m", "pytest", "-q", "tests"]),
    ("check two-stage router build", "two_stage_build"),
    ("check two-stage router validation", "two_stage_validate"),
]


def run_step(label: str, command: str | list[str]) -> int:
    resolved = _command_with_roots(command) if isinstance(command, str) else command
    print(f"[run] {label}: {subprocess.list2cmdline(resolved)}", flush=True)
    completed = subprocess.run(resolved, cwd=REPO_ROOT, env=os.environ.copy(), check=False)
    if completed.returncode != 0:
        print(f"[error] {label} failed with exit code {completed.returncode}", flush=True)
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
