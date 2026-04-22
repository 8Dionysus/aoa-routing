from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> object:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("schema_path", "example_path"),
    [
        (
            "schemas/titan_appserver_bridge_route.schema.json",
            "examples/titan_appserver_bridge_route.example.json",
        ),
        (
            "schemas/titan_console_route.schema.json",
            "examples/titan_console_route.example.json",
        ),
    ],
)
def test_titan_route_examples_validate(schema_path: str, example_path: str) -> None:
    Draft202012Validator(load_json(schema_path)).validate(load_json(example_path))


@pytest.mark.parametrize(
    ("schema_path", "payload"),
    [
        ("schemas/titan_appserver_bridge_route.schema.json", {}),
        (
            "schemas/titan_appserver_bridge_route.schema.json",
            {"route": ["unknown-repo"]},
        ),
        (
            "schemas/titan_console_route.schema.json",
            {"version": 1, "routes": [{"intent": "mutation", "titan": "Forge", "gate": "freewrite"}]},
        ),
        (
            "schemas/titan_console_route.schema.json",
            {"version": 1, "routes": [{"intent": 7, "titan": "Forge", "gate": "mutation"}]},
        ),
        (
            "schemas/titan_console_route.schema.json",
            {"version": 1, "routes": [{"intent": "structure", "titan": "Forge", "gate": None}]},
        ),
        (
            "schemas/titan_console_route.schema.json",
            {"version": 1, "routes": [{"intent": "judgment", "titan": "Atlas", "gate": "mutation"}]},
        ),
        (
            "schemas/titan_runtime_route.schema.json",
            {"version": 1, "intent": "orientation", "active_titans": [], "required_gates": []},
        ),
        (
            "schemas/titan_runtime_route.schema.json",
            {"version": 1, "intent": "implementation", "active_titans": ["Forge"], "required_gates": []},
        ),
        (
            "schemas/titan_runtime_route.schema.json",
            {"version": 1, "intent": "judgment", "active_titans": ["Delta"], "required_gates": []},
        ),
        (
            "schemas/titan_memory_route.schema.json",
            {"query": "find memory", "record_id": "memory:1", "source_ref": None, "owner_route": ["aoa-memo"]},
        ),
        (
            "schemas/titan_memory_route.schema.json",
            {"query": "find memory", "record_id": "memory:1", "owner_route": ["aoa-memo"]},
        ),
        (
            "schemas/titan_memory_route.schema.json",
            {"query": "find memory", "record_id": "memory:1", "session_id": "session:1", "owner_route": []},
        ),
    ],
)
def test_titan_route_schemas_reject_malformed_payloads(schema_path: str, payload: object) -> None:
    validator = Draft202012Validator(load_json(schema_path))

    with pytest.raises(ValidationError):
        validator.validate(payload)


@pytest.mark.parametrize(
    ("schema_path", "payload"),
    [
        (
            "schemas/titan_runtime_route.schema.json",
            {
                "version": 1,
                "intent": "implementation",
                "active_titans": ["Atlas", "Sentinel", "Mneme", "Forge"],
                "required_gates": ["mutation"],
            },
        ),
        (
            "schemas/titan_runtime_route.schema.json",
            {
                "version": 1,
                "intent": "verdict",
                "active_titans": ["Atlas", "Sentinel", "Mneme", "Delta"],
                "required_gates": ["judgment"],
            },
        ),
        (
            "schemas/titan_memory_route.schema.json",
            {
                "query": "find memory",
                "record_id": "memory:1",
                "session_id": "session:2026-04-22",
                "owner_route": ["aoa-memo"],
            },
        ),
    ],
)
def test_titan_route_schemas_accept_gated_or_located_payloads(
    schema_path: str, payload: object
) -> None:
    Draft202012Validator(load_json(schema_path)).validate(payload)
