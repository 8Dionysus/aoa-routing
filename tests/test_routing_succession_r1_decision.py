from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    REPO_ROOT
    / "docs"
    / "decisions"
    / "AOA-RT-D-0004-stage-producer-succession-to-aoa-sdk.md"
)


def test_succession_decision_keeps_predecessor_canonical_until_g5() -> None:
    text = DECISION.read_text(encoding="utf-8")

    assert "- Decision ID: AOA-RT-D-0004" in text
    assert "- Posture: accepted" in text
    assert "`aoa-routing` remains the sole\ncanonical producer" in text
    assert "Shadow output cannot publish" in text
    assert "This record does not authorize repository archive" in text


def test_succession_decision_preserves_abi_and_stronger_owners() -> None:
    text = DECISION.read_text(encoding="utf-8")

    assert "all fourteen public output paths" in text
    assert "`aoa_routing_thin_router_v1`" in text
    assert "changes producer ownership and provenance, not public\nartifact paths" in text
    assert "runtime owner\ncontinues to own activation and model/tool execution" in text
    assert "`AOA-SDK-D-0071`" in text


def test_active_route_docs_name_the_completed_switch_and_archive_boundary() -> None:
    required = {
        REPO_ROOT / "AGENTS.md": "AOA-RT-D-0004",
        REPO_ROOT / "README.md": "canonical routing producer",
        REPO_ROOT / "ROADMAP.md": "sdk_canonical",
        REPO_ROOT / "routing" / "AGENTS.md": "canonical ownership to `aoa-sdk`",
        REPO_ROOT / "routing" / "README.md": "final `v0.4.0` archive boundary",
    }

    for path, marker in required.items():
        assert marker in path.read_text(encoding="utf-8"), path


def test_nested_predecessor_routes_are_retired() -> None:
    source_home = (
        REPO_ROOT / "routing" / "source_home.manifest.json"
    ).read_text(encoding="utf-8")
    core_card = (REPO_ROOT / "routing" / "core" / "AGENTS.md").read_text(
        encoding="utf-8"
    )
    nested_release = (
        REPO_ROOT
        / "mechanics"
        / "release-support"
        / "parts"
        / "release-gate-routing"
        / "docs"
        / "releasing.md"
    ).read_text(encoding="utf-8")

    assert '"status": "retired"' in source_home
    assert "It owns no active changes." in core_card
    assert "do not\npublish or maintain this predecessor" in nested_release
    assert "Route every routing release request to\n`aoa-sdk`" in nested_release


def test_local_kag_owner_return_is_archived_and_redirected() -> None:
    for relative_path in (
        "kag/nodes/routing-source-home.json",
        "kag/nodes/routing-source-route.json",
        "kag/edges/source_returns_to_owner.json",
        "kag/indexes/provider_readiness_index.json",
        "kag/projections/mcp_source_return.json",
        "kag/receipts/validation_receipt.json",
    ):
        payload = json.loads(
            (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        )
        assert payload["status"] == "archived"
        assert payload["owner_return_route"] == {
            "repo": "aoa-routing",
            "surface": "README.md",
            "route_kind": "routing",
        }

    manifest = json.loads(
        (REPO_ROOT / "kag" / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["owner_return_routes"] == [
        {
            "repo": "aoa-routing",
            "surface": "README.md",
            "route_kind": "routing",
        }
    ]
    receipt = json.loads(
        (REPO_ROOT / "kag" / "receipts" / "validation_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    assert receipt["result"] == "routed"
