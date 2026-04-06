from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_readme_lists_full_read_only_verify_battery() -> None:
    readme = read_text("README.md")

    commands = [
        "python scripts/validate_router.py",
        "python scripts/build_router.py --check",
        "python -m pytest -q tests",
        "python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check",
        "python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills",
    ]
    for command in commands:
        assert command in readme

    assert readme.index(commands[0]) < readme.index(commands[1]) < readme.index(commands[2])


def test_contributor_and_agent_surfaces_use_exact_verify_commands() -> None:
    expected_fragments = [
        "python scripts/validate_router.py",
        "python scripts/build_router.py --check",
        "python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check",
        "python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills",
        "python -m pytest -q tests",
    ]

    for relative_path in [
        "AGENTS.md",
        "CONTRIBUTING.md",
        "generated/AGENTS.md",
        "scripts/AGENTS.md",
        "tests/AGENTS.md",
    ]:
        text = read_text(relative_path)
        for fragment in expected_fragments:
            assert fragment in text, f"{relative_path} missing {fragment}"
