from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_roadmap_federation_milestone_mentions_current_active_entry_kinds() -> None:
    roadmap = read_text("ROADMAP.md")
    federation_payload = json.loads(read_text("generated/federation_entrypoints.min.json"))

    for kind in ("source_route", "runtime_surface", "orientation_surface"):
        assert kind in federation_payload["active_entry_kinds"]
        assert f"`{kind}`" in roadmap


def test_roadmap_matches_current_v0_3_release_surfaces() -> None:
    readme = read_text("README.md")
    changelog = read_text("CHANGELOG.md")
    roadmap = read_text("ROADMAP.md")

    assert "v0.3.0" in readme
    assert "[0.3.0]" in changelog
    assert "v0.3.0" in roadmap

    for relative_path in (
        "generated/federation_entrypoints.min.json",
        "generated/return_navigation_hints.min.json",
        "generated/composite_stress_route_hints.min.json",
        "generated/tiny_model_entrypoints.json",
        "docs/decisions/AOA-RT-D-0003-owner-capability-routing.md",
        "mechanics/boundary-bridge/parts/federation-entry/docs/federation-entry-abi.md",
        "mechanics/antifragility/parts/composite-stress-routing/docs/playbook-stress-route-consumption.md",
        "mechanics/antifragility/parts/quarantine-routing/docs/kag-quarantine-route-hints.md",
        "mechanics/antifragility/parts/stress-routing/docs/stress-posture-routing.md",
        "mechanics/antifragility/parts/degraded-route-hints/docs/degraded-route-hints.md",
    ):
        assert (REPO_ROOT / relative_path).is_file()
        assert relative_path in roadmap

    for owner_surface in (
        "aoa-skills/generated/agent_skill_catalog.min.json",
        "aoa-skills/generated/capability_graph.json",
        "aoa-evals/generated/eval_catalog.min.json",
    ):
        assert owner_surface in roadmap

    assert "federation-mesh" in changelog
    assert "technique-kind second-cut" in roadmap
    assert "roadmap drift" in roadmap
    assert "task-local DAG" in roadmap


def test_roadmap_names_agon_gate_routing_surfaces() -> None:
    roadmap = read_text("ROADMAP.md")

    assert "### Milestone 10: Agon gate routing" in roadmap

    for relative_path in (
        "mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json",
        "mechanics/agon/parts/gate-routing/docs/gate-routing.md",
        "mechanics/agon/parts/gate-routing/docs/trigger-model.md",
        "mechanics/agon/parts/gate-routing/docs/decision-boundary.md",
        "mechanics/agon/parts/gate-routing/docs/assistant-escalation.md",
        "mechanics/agon/parts/gate-routing/docs/owner-handoffs.md",
        "mechanics/agon/parts/gate-routing/schemas/agon-gate-routing-registry.schema.json",
        "mechanics/agon/parts/gate-routing/schemas/agon-gate-trigger.schema.json",
        "mechanics/agon/parts/gate-routing/schemas/agon-gate-route-hint.schema.json",
        "mechanics/agon/parts/gate-routing/config/agon_gate_routing.config.json",
        "mechanics/agon/parts/gate-routing/examples/agon_gate_route_hint.example.json",
        "mechanics/agon/parts/gate-routing/scripts/build_agon_gate_routing_registry.py",
        "mechanics/agon/parts/gate-routing/scripts/validate_agon_gate_routing.py",
        "mechanics/agon/parts/gate-routing/tests/test_agon_gate_routing.py",
    ):
        assert (REPO_ROOT / relative_path).is_file()
        assert relative_path in roadmap
