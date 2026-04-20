from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_builder():
    path = ROOT / "scripts" / "build_agon_gate_routing_registry.py"
    spec = importlib.util.spec_from_file_location("build_agon_gate_routing_registry", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_agon_gate_registry_is_current():
    builder = load_builder()
    config = load_json(ROOT / "config" / "agon_gate_routing.seed.json")
    expected = json.dumps(
        builder.build_registry(config),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
    current = (ROOT / "generated" / "agon_gate_routing_registry.min.json").read_text(encoding="utf-8")
    assert current == expected


def test_agon_gate_registry_keeps_routing_thin():
    registry = load_json(ROOT / "generated" / "agon_gate_routing_registry.min.json")

    assert registry["owner_repo"] == "aoa-routing"
    assert registry["center_repo"] == "Agents-of-Abyss"
    assert registry["trigger_count"] >= 10
    assert registry["route_hint_count"] == registry["trigger_count"]

    stop_lines = set(registry["stop_lines"])
    assert "no_arena_session_creation" in stop_lines
    assert "no_verdict" in stop_lines
    assert "no_scar_write" in stop_lines
    assert "no_tos_promotion" in stop_lines

    for hint in registry["route_hints"]:
        assert hint["live_protocol"] is False
        assert hint["runtime_effect"] == "none"
        assert "open_arena" not in hint["assistant_allowed"]
        assert "become_contestant" not in hint["assistant_allowed"]
        assert "issue_verdict" not in hint["assistant_allowed"]
