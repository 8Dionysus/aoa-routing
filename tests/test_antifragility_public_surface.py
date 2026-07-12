from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> object:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def test_stress_navigation_example_validates_against_schema() -> None:
    schema = load_json("mechanics/antifragility/parts/degraded-route-hints/schemas/stress_navigation_hint_v1.json")
    example = load_json("mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.example.json")

    assert schema["$id"] == "https://aoa-routing/schemas/stress_navigation_hint_v1.json"
    Draft202012Validator(schema).validate(example)


def test_timeout_chaos_stress_navigation_example_validates_against_schema() -> None:
    schema = load_json("mechanics/antifragility/parts/degraded-route-hints/schemas/stress_navigation_hint_v1.json")
    example = load_json("mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.timeout-chaos.example.json")

    Draft202012Validator(schema).validate(example)


def test_skill_collision_chaos_stress_navigation_example_validates_against_schema() -> None:
    schema = load_json("mechanics/antifragility/parts/degraded-route-hints/schemas/stress_navigation_hint_v1.json")
    example = load_json("mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.skill-collision-chaos.example.json")

    Draft202012Validator(schema).validate(example)


def test_composite_stress_route_hint_example_validates_against_schema() -> None:
    schema = load_json("mechanics/antifragility/parts/composite-stress-routing/schemas/composite_stress_route_hint_v1.json")
    example = load_json("mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.example.json")

    Draft202012Validator(schema).validate(example)


def test_retrieval_outage_honesty_composite_example_validates_against_schema() -> None:
    schema = load_json("mechanics/antifragility/parts/composite-stress-routing/schemas/composite_stress_route_hint_v1.json")
    example = load_json("mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.retrieval-outage-honesty.example.json")

    Draft202012Validator(schema).validate(example)


def test_composite_stress_examples_route_to_current_owner_paths() -> None:
    examples = (
        load_json(
            "mechanics/antifragility/parts/composite-stress-routing/examples/"
            "composite_stress_route_hint.example.json"
        ),
        load_json(
            "mechanics/antifragility/parts/composite-stress-routing/examples/"
            "composite_stress_route_hint.retrieval-outage-honesty.example.json"
        ),
    )
    required_route_fragments = (
        "aoa-playbooks:mechanics/antifragility/parts/",
        "aoa-kag:mechanics/antifragility/parts/",
        "aoa-memo:mechanics/antifragility/parts/recovery-pattern-memory/",
        "repo:aoa-evals/evals/comparison/longitudinal-window/"
        "aoa-stress-recovery-window/",
    )

    for example in examples:
        serialized = json.dumps(example, sort_keys=True)
        for fragment in required_route_fragments:
            assert fragment in serialized
        assert "repo:aoa-evals/bundles/aoa-stress-recovery-window/" not in serialized


def test_generated_stress_routes_use_current_stats_owner_refs() -> None:
    composite = load_json("generated/composite_stress_route_hints.min.json")
    stats_regrounding = load_json("generated/stats_regrounding_hints.min.json")

    hint = composite["hints"][0]
    assert hint["source_priority"]["owner_receipt_refs"] == [
        "repo:ATM10-Agent/examples/stressor_receipt.retrieval_only_fallback.example.json"
    ]
    assert hint["source_priority"]["proof_refs"] == [
        "repo:aoa-evals/evals/comparison/longitudinal-window/"
        "aoa-stress-recovery-window/reports/example-report.json"
    ]

    regrounding_hint = next(
        item
        for item in stats_regrounding["hints"]
        if item["surface_name"] == "stress_recovery_window_summary"
    )
    assert regrounding_hint["owner_truth_inputs"][:2] == [
        "aoa-evals/evals/comparison/longitudinal-window/"
        "aoa-stress-recovery-window/EVAL.md",
        "aoa-evals/evals/comparison/longitudinal-window/"
        "aoa-stress-recovery-window/reports/example-report.json",
    ]
    assert "future activated" not in json.dumps(regrounding_hint)


def test_antifragility_surfaces_are_discoverable_and_keep_routing_thin() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    routing_doc = (
        REPO_ROOT
        / "mechanics"
        / "antifragility"
        / "parts"
        / "stress-routing"
        / "docs"
        / "stress-posture-routing.md"
    ).read_text(encoding="utf-8")
    chaos_doc = (
        REPO_ROOT
        / "mechanics"
        / "antifragility"
        / "parts"
        / "stress-routing"
        / "docs"
        / "routing-stress-chaos.md"
    ).read_text(encoding="utf-8")
    degraded_doc = (
        REPO_ROOT
        / "mechanics"
        / "antifragility"
        / "parts"
        / "degraded-route-hints"
        / "docs"
        / "degraded-route-hints.md"
    ).read_text(encoding="utf-8")
    playbook_doc = (
        REPO_ROOT
        / "mechanics"
        / "antifragility"
        / "parts"
        / "composite-stress-routing"
        / "docs"
        / "playbook-stress-route-consumption.md"
    ).read_text(encoding="utf-8")
    kag_doc = (
        REPO_ROOT
        / "mechanics"
        / "antifragility"
        / "parts"
        / "quarantine-routing"
        / "docs"
        / "kag-quarantine-route-hints.md"
    ).read_text(encoding="utf-8")

    for fragment in [
        "mechanics/antifragility/parts/stress-routing/docs/stress-posture-routing.md",
        "mechanics/antifragility/parts/degraded-route-hints/docs/degraded-route-hints.md",
        "mechanics/antifragility/parts/stress-routing/docs/routing-stress-chaos.md",
        "mechanics/antifragility/parts/degraded-route-hints/schemas/stress_navigation_hint_v1.json",
        "mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.example.json",
        "mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.timeout-chaos.example.json",
        "mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.skill-collision-chaos.example.json",
        "generated/composite_stress_route_hints.min.json",
        "mechanics/antifragility/parts/composite-stress-routing/docs/playbook-stress-route-consumption.md",
        "mechanics/antifragility/parts/quarantine-routing/docs/kag-quarantine-route-hints.md",
        "mechanics/antifragility/parts/composite-stress-routing/schemas/composite_stress_route_hint_v1.json",
        "mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.example.json",
        "mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.retrieval-outage-honesty.example.json",
        "routing/two-stage-skill-selection/config/two_stage_router_precision_cases.jsonl",
    ]:
        assert fragment in readme

    assert "do not make routing the source of stress meaning" in routing_doc
    assert "Do not turn `aoa-routing` into a health oracle" in chaos_doc
    assert "weak or empty shortlist -> `no-skill`" in chaos_doc
    assert "They are a stress overlay, not a new sovereign router." in degraded_doc
    assert "Use structured playbook lane and re-entry gate surfaces, not live `PLAYBOOK.md` parsing." in playbook_doc
    assert "Quarantine hints stay additive and never replace KAG authored truth." in kag_doc
