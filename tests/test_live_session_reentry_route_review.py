from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
import pytest

from scripts import validate_router


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "live-session-reentry-route-review.schema.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "live_session_reentry_route_review.example.json"


def load_schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_example() -> dict[str, object]:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def copy_surface_file(tmp_repo_root: Path, relative_path: str) -> None:
    destination = tmp_repo_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text((REPO_ROOT / relative_path).read_text(encoding="utf-8"), encoding="utf-8")


def test_live_session_reentry_route_review_example_validates() -> None:
    schema = load_schema()
    example = load_example()
    Draft202012Validator(schema).validate(example)


def test_live_session_reentry_route_review_schema_rejects_router_owned_primary_action() -> None:
    schema = load_schema()
    example = load_example()
    example["primary_action"] = {
        "verb": "inspect",
        "target_repo": "aoa-routing",
        "target_surface": "generated/return_navigation_hints.min.json",
    }

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(example)


def test_live_session_reentry_route_review_references_budget_without_owning_it() -> None:
    example = load_example()

    assert example["budget_ref"] == (
        "Agents-of-Abyss:mechanics/experience/parts/continuity-context/CONTRACT.md#stronger-owner-split"
    )
    assert example["fallback_action"]["target_repo"] == "aoa-evals"
    assert example["fallback_action"]["target_surface"] == "docs/TRACE_EVAL_BRIDGE.md"
    assert example["primary_action"]["target_repo"] == "aoa-agents"
    assert example["secondary_action"]["target_repo"] == "aoa-memo"


def test_validate_router_accepts_live_session_reentry_route_review_surface() -> None:
    issues: list[validate_router.ValidationIssue] = []

    validate_router.validate_live_session_reentry_route_review(REPO_ROOT, issues)

    assert issues == []


def test_validate_router_rejects_missing_cross_repo_anchor(tmp_path: Path) -> None:
    tmp_root = tmp_path
    repo_root = tmp_root / "aoa-routing"
    for relative_path in (
        "README.md",
        "docs/LIVE_SESSION_REENTRY_ROUTE_REVIEW.md",
        "schemas/live-session-reentry-route-review.schema.json",
        "examples/live_session_reentry_route_review.example.json",
    ):
        copy_surface_file(repo_root, relative_path)

    (tmp_root / "aoa-agents" / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_root / "aoa-agents" / "docs" / "SELF_AGENCY_CONTINUITY_LANE.md").write_text(
        "# Self-Agency Continuity Lane\n",
        encoding="utf-8",
    )
    (tmp_root / "aoa-memo" / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_root / "aoa-memo" / "docs" / "SELF_AGENCY_CONTINUITY_WRITEBACK.md").write_text(
        "# SELF_AGENCY_CONTINUITY_WRITEBACK\n",
        encoding="utf-8",
    )
    (tmp_root / "aoa-evals" / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_root / "aoa-evals" / "docs" / "TRACE_EVAL_BRIDGE.md").write_text(
        "# Trace Eval Bridge\n",
        encoding="utf-8",
    )
    (tmp_root / "Agents-of-Abyss" / "mechanics" / "experience" / "parts" / "continuity-context").mkdir(
        parents=True,
        exist_ok=True,
    )
    (
        tmp_root
        / "Agents-of-Abyss"
        / "mechanics"
        / "experience"
        / "parts"
        / "continuity-context"
        / "CONTRACT.md"
    ).write_text(
        "# Continuity Context Contract\n",
        encoding="utf-8",
    )

    issues: list[validate_router.ValidationIssue] = []
    validate_router.validate_live_session_reentry_route_review(repo_root, issues)

    assert any(
        "budget_ref anchor 'stronger-owner-split' was not found" in issue.message for issue in issues
    )


def test_validate_router_reports_missing_contract_surface(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    for relative_path in (
        "README.md",
        "schemas/live-session-reentry-route-review.schema.json",
        "examples/live_session_reentry_route_review.example.json",
    ):
        copy_surface_file(repo_root, relative_path)

    issues: list[validate_router.ValidationIssue] = []
    validate_router.validate_live_session_reentry_route_review(repo_root, issues)

    assert issues == [
        validate_router.ValidationIssue(
            "docs/LIVE_SESSION_REENTRY_ROUTE_REVIEW.md",
            "missing required live-session reentry contract surface",
        )
    ]


def test_validate_router_reports_malformed_contract_json(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    for relative_path in (
        "README.md",
        "docs/LIVE_SESSION_REENTRY_ROUTE_REVIEW.md",
        "examples/live_session_reentry_route_review.example.json",
    ):
        copy_surface_file(repo_root, relative_path)

    schema_path = repo_root / "schemas" / "live-session-reentry-route-review.schema.json"
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text("{\n", encoding="utf-8")

    issues: list[validate_router.ValidationIssue] = []
    validate_router.validate_live_session_reentry_route_review(repo_root, issues)

    assert len(issues) == 1
    assert issues[0].location == "live_session_reentry_route_review.example.json"
    assert "invalid JSON" in issues[0].message
