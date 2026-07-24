from __future__ import annotations

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


def test_active_route_docs_name_accepted_succession_without_claiming_switch() -> None:
    required = {
        REPO_ROOT / "AGENTS.md": "AOA-RT-D-0004",
        REPO_ROOT / "README.md": "predecessor_canonical",
        REPO_ROOT / "ROADMAP.md": "Accepted Succession Contour",
        REPO_ROOT / "routing" / "AGENTS.md": "G5",
        REPO_ROOT / "routing" / "README.md": "maintenance-only",
    }

    for path, marker in required.items():
        assert marker in path.read_text(encoding="utf-8"), path
