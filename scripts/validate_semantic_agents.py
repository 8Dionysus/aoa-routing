#!/usr/bin/env python3
"""Validate Pack 4 semantic-layer AGENTS.md guidance for aoa-routing."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AgentsDocSpec:
    path: Path
    required_snippets: tuple[str, ...]


REQUIRED_DOCS: tuple[AgentsDocSpec, ...] = (
    AgentsDocSpec(
        Path('.agents/skills/AGENTS.md'),
        (
            'routing-layer maintenance',
            'Source repos own meaning. Routing repo owns navigation.',
            'low-context',
            'public-safe',
            'validate_router.py',
            'python scripts/validate_semantic_agents.py',
        ),
    ),
    AgentsDocSpec(
        Path('config/AGENTS.md'),
        (
            'routing build',
            'source-owned meaning',
            'low-context posture',
            'build_router.py --check',
            'validate_router.py',
            'python scripts/validate_semantic_agents.py',
        ),
    ),
    AgentsDocSpec(
        Path('docs/AGENTS.md'),
        (
            'routing ABI',
            'navigation semantics',
            'hints into authority',
            'owner repository',
            'validate_router.py',
            'python scripts/validate_semantic_agents.py',
        ),
    ),
    AgentsDocSpec(
        Path('examples/AGENTS.md'),
        (
            'schema-backed',
            'source authority',
            'low-context',
            'public-safe',
            'validate_router.py',
            'python scripts/validate_semantic_agents.py',
        ),
    ),
)


def _display(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def validate(repo_root: Path = REPO_ROOT) -> list[str]:
    issues: list[str] = []
    for spec in REQUIRED_DOCS:
        path = repo_root / spec.path
        if not path.is_file():
            issues.append(f"{spec.path.as_posix()}: file is missing")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.strip().startswith("# AGENTS.md"):
            issues.append(f"{spec.path.as_posix()}: must start with '# AGENTS.md'")
        for snippet in spec.required_snippets:
            if snippet not in text:
                issues.append(
                    f"{spec.path.as_posix()}: missing required snippet {snippet!r}"
                )
    return issues


def main() -> int:
    issues = validate(REPO_ROOT)
    if issues:
        print("Pack 4 semantic AGENTS validation failed.", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print(f"[ok] Pack 4 semantic AGENTS docs are present and shaped: {len(REQUIRED_DOCS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
