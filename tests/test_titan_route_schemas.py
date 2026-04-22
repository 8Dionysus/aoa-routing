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
    ],
)
def test_titan_route_schemas_reject_malformed_payloads(schema_path: str, payload: object) -> None:
    validator = Draft202012Validator(load_json(schema_path))

    with pytest.raises(ValidationError):
        validator.validate(payload)
