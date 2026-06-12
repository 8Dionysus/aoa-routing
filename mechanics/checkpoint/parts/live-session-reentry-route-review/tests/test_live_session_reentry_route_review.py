from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scripts import validate_router


PART_ROOT = REPO_ROOT / "mechanics" / "checkpoint" / "parts" / "live-session-reentry-route-review"
DOC_RELATIVE_PATH = "mechanics/checkpoint/parts/live-session-reentry-route-review/docs/live-session-reentry-route-review.md"
SCHEMA_RELATIVE_PATH = "mechanics/checkpoint/parts/live-session-reentry-route-review/schemas/live-session-reentry-route-review.schema.json"
EXAMPLE_RELATIVE_PATH = "mechanics/checkpoint/parts/live-session-reentry-route-review/examples/live_session_reentry_route_review.example.json"
SCHEMA_PATH = REPO_ROOT / SCHEMA_RELATIVE_PATH
EXAMPLE_PATH = REPO_ROOT / EXAMPLE_RELATIVE_PATH


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
    assert (
        example["fallback_action"]["target_surface"]
        == "mechanics/audit/parts/artifact-verdict-hooks/docs/TRACE_EVAL_BRIDGE.md"
    )
    assert example["primary_action"]["target_repo"] == "aoa-agents"
    assert example["secondary_action"]["target_repo"] == "aoa-memo"
    assert example["secondary_action"]["target_surface"] == (
        "mechanics/writeback/docs/SELF_AGENCY_CONTINUITY_WRITEBACK.md"
    )


def test_validate_router_accepts_live_session_reentry_route_review_surface() -> None:
    issues: list[validate_router.ValidationIssue] = []

    validate_router.validate_live_session_reentry_route_review(REPO_ROOT, issues)

    assert issues == []


def test_validate_router_rejects_missing_cross_repo_anchor(tmp_path: Path) -> None:
    tmp_root = tmp_path
    repo_root = tmp_root / "aoa-routing"
    for relative_path in (
        "README.md",
        DOC_RELATIVE_PATH,
        SCHEMA_RELATIVE_PATH,
        EXAMPLE_RELATIVE_PATH,
    ):
        copy_surface_file(repo_root, relative_path)

    continuity_doc = (
        tmp_root
        / "aoa-agents"
        / "mechanics/checkpoint/parts/continuity-lane/docs/self-agency-continuity-lane.md"
    )
    continuity_doc.parent.mkdir(parents=True, exist_ok=True)
    continuity_doc.write_text(
        "# Self-Agency Continuity Lane\n",
        encoding="utf-8",
    )
    checkpoint_schema = (
        tmp_root
        / "aoa-memo"
        / "mechanics/checkpoint/parts/checkpoint-carry-contract/schemas/inquiry_checkpoint.schema.json"
    )
    checkpoint_schema.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_schema.write_text(
        "{}\n",
        encoding="utf-8",
    )
    (tmp_root / "aoa-memo" / "mechanics" / "writeback" / "docs").mkdir(
        parents=True,
        exist_ok=True,
    )
    (
        tmp_root
        / "aoa-memo"
        / "mechanics"
        / "writeback"
        / "docs"
        / "SELF_AGENCY_CONTINUITY_WRITEBACK.md"
    ).write_text(
        "# SELF_AGENCY_CONTINUITY_WRITEBACK\n",
        encoding="utf-8",
    )
    trace_bridge = (
        tmp_root
        / "aoa-evals"
        / "mechanics/audit/parts/artifact-verdict-hooks/docs/TRACE_EVAL_BRIDGE.md"
    )
    trace_bridge.parent.mkdir(parents=True, exist_ok=True)
    trace_bridge.write_text(
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
        SCHEMA_RELATIVE_PATH,
        EXAMPLE_RELATIVE_PATH,
    ):
        copy_surface_file(repo_root, relative_path)

    issues: list[validate_router.ValidationIssue] = []
    validate_router.validate_live_session_reentry_route_review(repo_root, issues)

    assert issues == [
        validate_router.ValidationIssue(
            DOC_RELATIVE_PATH,
            "missing required live-session reentry contract surface",
        )
    ]


def test_validate_router_reports_malformed_contract_json(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    for relative_path in (
        "README.md",
        DOC_RELATIVE_PATH,
        EXAMPLE_RELATIVE_PATH,
    ):
        copy_surface_file(repo_root, relative_path)

    schema_path = repo_root / SCHEMA_RELATIVE_PATH
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text("{\n", encoding="utf-8")

    issues: list[validate_router.ValidationIssue] = []
    validate_router.validate_live_session_reentry_route_review(repo_root, issues)

    assert len(issues) == 1
    assert issues[0].location == "live_session_reentry_route_review.example.json"
    assert "invalid JSON" in issues[0].message
