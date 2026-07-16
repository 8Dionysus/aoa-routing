from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIMARY_COMMAND_DOCS = frozenset(
    {"mechanics/release-support/parts/release-gate-routing/docs/releasing.md"}
)
EXECUTABLE_MARKDOWN_PREFIXES = (".agents/skills/",)
SHELL_FENCE_PATTERN = re.compile(
    r"^ {0,3}```(?:bash|console|sh|shell|zsh)(?:\s+.*)?$",
    re.IGNORECASE | re.MULTILINE,
)
REPO_COMMAND_LINE_PATTERN = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?`?(?:"
    r"python3?(?:[ \t]+-m)?[ \t]+|pytest(?=[ \t])|"
    r"uv[ \t]+run[ \t]+pytest\b|git[ \t]+(?:status|diff)\b|"
    r"aoa[ \t]+release\b)",
    re.IGNORECASE | re.MULTILINE,
)
INLINE_REPO_COMMAND_PATTERN = re.compile(
    r"`(?:python3?(?:\s+-m)?\s+|pytest(?=\s)|"
    r"uv\s+run\s+pytest\b|git\s+(?:status|diff)\b|"
    r"aoa\s+release\b)[^`]+`",
    re.IGNORECASE,
)


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def tracked_markdown_paths() -> tuple[Path, ...]:
    completed = subprocess.run(
        ("git", "ls-files", "--", "*.md"),
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(
        path
        for line in completed.stdout.splitlines()
        if line and (path := Path(line)) and (REPO_ROOT / path).is_file()
    )


def markdown_command_violations(content: str) -> set[str]:
    violations: set[str] = set()
    if SHELL_FENCE_PATTERN.search(content):
        violations.add("shell command block")
    if REPO_COMMAND_LINE_PATTERN.search(content):
        violations.add("repo command line")
    if INLINE_REPO_COMMAND_PATTERN.search(content):
        violations.add("inline repo command")
    return violations


def test_readme_routes_verify_battery_to_agents() -> None:
    readme = read_text("README.md")
    root_agents = read_text("AGENTS.md")

    commands = [
        "python scripts/validate_router.py",
        "python scripts/build_router.py --check",
        "python scripts/generate_decision_indexes.py --check",
        "python scripts/validate_decision_records.py",
        "python -m pytest -q tests",
    ]
    for command in commands:
        assert command not in readme
        assert command in root_agents

    assert "[AGENTS.md](AGENTS.md#verify)" in readme
    assert "scripts/release_check.py" in readme


def test_contributor_and_agent_surfaces_use_exact_verify_commands() -> None:
    core_fragments = [
        "python scripts/validate_router.py",
        "python scripts/build_router.py --check",
        "python -m pytest -q tests",
    ]

    for relative_path in [
        "AGENTS.md",
        "generated/AGENTS.md",
        "scripts/AGENTS.md",
        "tests/AGENTS.md",
    ]:
        text = read_text(relative_path)
        for fragment in core_fragments:
            assert fragment in text, f"{relative_path} missing {fragment}"

    decision_fragments = [
        "python scripts/generate_decision_indexes.py --check",
        "python scripts/validate_decision_records.py",
    ]
    for relative_path in [
        "AGENTS.md",
        "scripts/AGENTS.md",
        "tests/AGENTS.md",
        "docs/decisions/AGENTS.md",
    ]:
        text = read_text(relative_path)
        for fragment in decision_fragments:
            assert fragment in text, f"{relative_path} missing {fragment}"

    contributing = read_text("CONTRIBUTING.md")
    assert "[AGENTS.md](AGENTS.md#verify)" in contributing
    for fragment in (*core_fragments, *decision_fragments):
        assert fragment not in contributing


def test_non_owner_markdown_routes_runnable_commands_to_command_owners() -> None:
    offenders: list[str] = []
    for relative_path in tracked_markdown_paths():
        route = relative_path.as_posix()
        if route.startswith(EXECUTABLE_MARKDOWN_PREFIXES):
            continue
        if relative_path.name in {"AGENTS.md", "VALIDATION.md"}:
            continue
        if route in PRIMARY_COMMAND_DOCS:
            continue
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for violation in sorted(markdown_command_violations(content)):
            offenders.append(f"{route}: {violation}")

    assert offenders == []


def test_markdown_command_guard_rejects_scattered_command_forms() -> None:
    content = """# Drift

```bash
python scripts/validate_router.py
```

- `python -m pytest -q tests`
- git status -sb
"""

    assert markdown_command_violations(content) == {
        "inline repo command",
        "repo command line",
        "shell command block",
    }


def test_readme_and_roadmap_expose_agon_gate_routing_surfaces() -> None:
    readme = read_text("README.md")
    roadmap = read_text("ROADMAP.md")
    changelog = read_text("CHANGELOG.md")
    registry = read_text("mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json")

    assert "mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json" in readme
    assert "mechanics/agon/parts/gate-routing/docs/gate-routing.md" in readme
    assert "Agon gate routing" in roadmap
    assert "Agon gate routing" in changelog
    assert "\"live_protocol\":false" in registry
    assert "\"runtime_effect\":\"none\"" in registry
