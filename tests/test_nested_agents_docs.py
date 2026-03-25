from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate_nested_agents  # noqa: E402
import validate_router  # noqa: E402


def materialize_valid_agents(repo_root: Path) -> None:
    for relative_path, required_phrases in validate_nested_agents.REQUIRED_AGENTS.items():
        path = repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# AGENTS.md\n\n" + "\n".join(f"- {phrase}" for phrase in required_phrases) + "\n",
            encoding="utf-8",
        )


def test_nested_agents_docs_are_present_and_shaped() -> None:
    assert validate_nested_agents.run_validation(REPO_ROOT) == []


def test_nested_agents_validator_reports_missing_file(tmp_path: Path) -> None:
    materialize_valid_agents(tmp_path)
    missing_path = tmp_path / "generated" / "AGENTS.md"
    missing_path.unlink()

    issues = validate_nested_agents.run_validation(tmp_path)

    assert ("generated/AGENTS.md", "missing required nested AGENTS.md") in issues


def test_nested_agents_validator_reports_missing_anchor_phrase(tmp_path: Path) -> None:
    materialize_valid_agents(tmp_path)
    target_path = tmp_path / "tests" / "AGENTS.md"
    target_path.write_text(
        "# AGENTS.md\n\nTest surface without its required anchors.\n",
        encoding="utf-8",
    )

    issues = validate_nested_agents.run_validation(tmp_path)

    assert any(
        location == "tests/AGENTS.md"
        and "tests/test_route_walkthroughs.py" in message
        for location, message in issues
    )


def test_validate_router_main_includes_nested_agents_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    class Args:
        generated_dir = Path("/tmp/generated")
        techniques_root = Path("/tmp/aoa-techniques")
        skills_root = Path("/tmp/aoa-skills")
        evals_root = Path("/tmp/aoa-evals")
        memo_root = Path("/tmp/aoa-memo")
        agents_root = Path("/tmp/aoa-agents")
        aoa_root = Path("/tmp/Agents-of-Abyss")
        playbooks_root = Path("/tmp/aoa-playbooks")
        kag_root = Path("/tmp/aoa-kag")
        tos_root = Path("/tmp/Tree-of-Sophia")

    monkeypatch.setattr(validate_router, "parse_args", lambda: Args())
    monkeypatch.setattr(validate_router, "validate_generated_outputs", lambda *args: [])
    monkeypatch.setattr(
        validate_nested_agents,
        "run_validation",
        lambda repo_root=None: [("generated/AGENTS.md", "missing required phrase: python scripts/build_router.py")],
    )

    exit_code = validate_router.main()

    assert exit_code == 1
