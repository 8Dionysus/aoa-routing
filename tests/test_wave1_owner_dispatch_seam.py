from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "owner-dispatch-seam.schema.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "owner_dispatch_seam.example.json"
DOC_PATH = REPO_ROOT / "docs" / "AGON_GATE_DECISION_BOUNDARY.md"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def test_owner_dispatch_seam_example_validates() -> None:
    schema = load_json(SCHEMA_PATH)
    example = load_json(EXAMPLE_PATH)
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert isinstance(schema, dict)
    assert isinstance(example, dict)

    validator = Draft202012Validator(schema)
    errors = [error.message for error in validator.iter_errors(example)]

    assert errors == []
    assert "route_signal" in doc
    assert "route_decision" in doc
    assert "owner_dispatch" in doc
    assert example["owner_dispatch"]["owner_repo"] == "aoa-agents"
