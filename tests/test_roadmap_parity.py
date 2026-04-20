from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_roadmap_federation_milestone_mentions_current_active_entry_kinds() -> None:
    roadmap = read_text("ROADMAP.md")
    federation_payload = json.loads(read_text("generated/federation_entrypoints.min.json"))

    for kind in ("seed", "runtime_surface", "orientation_surface"):
        assert kind in federation_payload["active_entry_kinds"]
        assert f"`{kind}`" in roadmap


def test_roadmap_matches_current_v0_2_release_surfaces() -> None:
    readme = read_text("README.md")
    changelog = read_text("CHANGELOG.md")
    roadmap = read_text("ROADMAP.md")

    assert "v0.2.1" in readme
    assert "[0.2.1]" in changelog
    assert "v0.2.1" in roadmap

    for relative_path in (
        "generated/federation_entrypoints.min.json",
        "generated/return_navigation_hints.min.json",
        "generated/composite_stress_route_hints.min.json",
        "generated/tiny_model_entrypoints.json",
        "generated/two_stage_skill_entrypoints.json",
        "generated/two_stage_router_manifest.json",
        "generated/two_stage_router_eval_cases.jsonl",
        "docs/FEDERATION_ENTRY_ABI.md",
        "docs/TWO_STAGE_SKILL_SELECTION.md",
        "docs/PLAYBOOK_STRESS_ROUTE_CONSUMPTION.md",
        "docs/KAG_QUARANTINE_ROUTE_HINTS.md",
        "docs/STRESS_POSTURE_ROUTING.md",
        "docs/DEGRADED_ROUTE_HINTS.md",
    ):
        assert (REPO_ROOT / relative_path).is_file()
        assert relative_path in roadmap

    assert "federation-mesh" in changelog
    assert "technique-kind second-cut" in roadmap
    assert "roadmap drift" in roadmap
