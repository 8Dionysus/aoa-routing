from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> object:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def test_stress_navigation_example_validates_against_schema() -> None:
    schema = load_json("schemas/stress_navigation_hint_v1.json")
    example = load_json("examples/stress_navigation_hint.example.json")

    Draft202012Validator(schema).validate(example)


def test_composite_stress_route_hint_example_validates_against_schema() -> None:
    schema = load_json("schemas/composite_stress_route_hint_v1.json")
    example = load_json("examples/composite_stress_route_hint.example.json")

    Draft202012Validator(schema).validate(example)


def test_antifragility_surfaces_are_discoverable_and_keep_routing_thin() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    routing_doc = (REPO_ROOT / "docs" / "STRESS_POSTURE_ROUTING.md").read_text(encoding="utf-8")
    degraded_doc = (REPO_ROOT / "docs" / "DEGRADED_ROUTE_HINTS.md").read_text(encoding="utf-8")
    playbook_doc = (REPO_ROOT / "docs" / "PLAYBOOK_STRESS_ROUTE_CONSUMPTION.md").read_text(
        encoding="utf-8"
    )
    kag_doc = (REPO_ROOT / "docs" / "KAG_QUARANTINE_ROUTE_HINTS.md").read_text(
        encoding="utf-8"
    )

    for fragment in [
        "docs/STRESS_POSTURE_ROUTING.md",
        "docs/DEGRADED_ROUTE_HINTS.md",
        "schemas/stress_navigation_hint_v1.json",
        "examples/stress_navigation_hint.example.json",
        "generated/composite_stress_route_hints.min.json",
        "docs/PLAYBOOK_STRESS_ROUTE_CONSUMPTION.md",
        "docs/KAG_QUARANTINE_ROUTE_HINTS.md",
        "schemas/composite_stress_route_hint_v1.json",
        "examples/composite_stress_route_hint.example.json",
    ]:
        assert fragment in readme

    assert "do not make routing the source of stress meaning" in routing_doc
    assert "They are a stress overlay, not a new sovereign router." in degraded_doc
    assert "Use structured playbook lane and re-entry gate surfaces, not live `PLAYBOOK.md` parsing." in playbook_doc
    assert "Quarantine hints stay additive and never replace KAG authored truth." in kag_doc
