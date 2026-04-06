#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import TypeAlias

REPO_ROOT = Path(__file__).resolve().parents[1]
Issue: TypeAlias = tuple[str, str]

REQUIRED_AGENTS: dict[str, tuple[str, ...]] = {
    "generated/AGENTS.md": (
        "cross_repo_registry.min.json",
        "aoa_router.min.json",
        "task_to_surface_hints.json",
        "task_to_tier_hints.json",
        "quest_dispatch_hints.min.json",
        "federation_entrypoints.min.json",
        "tiny_model_entrypoints.json",
        "Do not hand-edit",
        "python scripts/build_router.py",
        "python scripts/validate_router.py",
        "python scripts/build_router.py --check",
        "python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills",
        "python -m pytest -q tests",
    ),
    "schemas/AGENTS.md": (
        "aoa-router.schema.json",
        "cross-repo-registry.schema.json",
        "router-entry.schema.json",
        "federation-entrypoints.schema.json",
        "quest_dispatch_hint.schema.json",
        "quest-dispatch-hints.schema.json",
        "tiny-model-entrypoints.schema.json",
        "contract change",
        "python scripts/validate_router.py",
    ),
    "scripts/AGENTS.md": (
        "build_router.py",
        "router_core.py",
        "validate_router.py",
        "Source repos own meaning. Routing repo owns navigation.",
        "deterministic",
        "python scripts/build_router.py",
        "python scripts/build_router.py --check",
        "python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills",
        "python -m pytest -q tests",
    ),
    "tests/AGENTS.md": (
        "tests/fixtures",
        "tests/test_build_router.py",
        "tests/test_validate_router.py",
        "tests/test_route_walkthroughs.py",
        "source-owned surfaces",
        "walkthroughs",
        "python scripts/build_router.py --check",
        "python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills",
        "python -m pytest -q tests",
    ),
}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def run_validation(repo_root: Path | None = None) -> list[Issue]:
    repo_root = repo_root or REPO_ROOT
    issues: list[Issue] = []

    for relative_path, required_phrases in REQUIRED_AGENTS.items():
        path = repo_root / relative_path
        if not path.is_file():
            issues.append((relative_path, "missing required nested AGENTS.md"))
            continue

        raw_text = path.read_text(encoding="utf-8")
        stripped = raw_text.strip()
        if not stripped.startswith("# AGENTS.md"):
            issues.append((relative_path, "missing '# AGENTS.md' heading"))

        text = normalize(raw_text)
        for phrase in required_phrases:
            if normalize(phrase) not in text:
                issues.append((relative_path, f"missing required phrase: {phrase}"))

    return issues


def main() -> int:
    issues = run_validation(REPO_ROOT)
    if issues:
        print("Nested AGENTS docs check failed.")
        for location, message in issues:
            print(f"- {location}: {message}")
        return 1

    print(f"Nested AGENTS docs check passed for {len(REQUIRED_AGENTS)} directories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
