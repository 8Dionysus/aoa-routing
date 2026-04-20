#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "generated" / "agon_gate_routing_registry.min.json"
CONFIG_PATH = ROOT / "config" / "agon_gate_routing.seed.json"

FORBIDDEN_HINT_FIELDS = {
    "arena_session",
    "sealed_commit",
    "verdict",
    "scar",
    "retention",
    "rank_mutation",
    "tos_promotion",
}

FORBIDDEN_ASSISTANT_RIGHTS = {
    "become_contestant",
    "issue_verdict",
    "grant_closure",
    "initiate_summon",
    "write_scar",
    "mutate_rank",
    "promote_to_tos",
    "promote_to_tree_of_sophia",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def optional_dependency_report() -> list[str]:
    reports: list[str] = []
    center_root = ROOT.parent / "Agents-of-Abyss"
    lawful = center_root / "generated" / "agon_lawful_move_registry.min.json"
    owner = center_root / "generated" / "agon_move_owner_binding_registry.min.json"
    formation = ROOT.parent / "aoa-agents" / "generated" / "agent_formation_trial.min.json"

    if lawful.exists():
        reports.append("found center lawful move registry")
    else:
        reports.append("optional center lawful move registry not found")

    if owner.exists():
        reports.append("found center move owner binding registry")
    else:
        reports.append("optional Wave IV owner binding registry not found")

    if formation.exists():
        reports.append("found aoa-agents formation trial")
    else:
        reports.append("optional aoa-agents formation trial not found")

    return reports


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_agon_gate_routing_registry.py"), "--check"],
        check=True,
    )

    config = load_json(CONFIG_PATH)
    registry = load_json(REGISTRY_PATH)

    require(registry["schema_version"] == "agon_gate_routing_registry.v1", "wrong schema version")
    require(registry["owner_repo"] == "aoa-routing", "routing registry must be owned by aoa-routing")
    require(registry["center_repo"] == "Agents-of-Abyss", "center repo must remain Agents-of-Abyss")
    require(registry["trigger_count"] == len(registry["triggers"]), "trigger_count mismatch")
    require(registry["route_hint_count"] == len(registry["route_hints"]), "route_hint_count mismatch")
    require(registry["trigger_count"] >= 10, "expected a broad pre-protocol trigger set")

    trigger_ids = [trigger["trigger_id"] for trigger in registry["triggers"]]
    require(len(trigger_ids) == len(set(trigger_ids)), "duplicate trigger_id")

    hint_ids = [hint["hint_id"] for hint in registry["route_hints"]]
    require(len(hint_ids) == len(set(hint_ids)), "duplicate hint_id")

    lawful_moves = set(config["lawful_moves_known"])
    require("escalate_to_agon_gate" in lawful_moves, "missing escalate_to_agon_gate lawful move")

    trigger_by_id = {trigger["trigger_id"]: trigger for trigger in registry["triggers"]}

    for hint in registry["route_hints"]:
        require(hint["trigger_id"] in trigger_by_id, f"hint references unknown trigger: {hint['hint_id']}")
        require(hint["live_protocol"] is False, f"hint must remain pre-protocol: {hint['hint_id']}")
        require(hint["runtime_effect"] == "none", f"hint must not have runtime effect: {hint['hint_id']}")
        require("open_arena" not in hint.get("assistant_allowed", []), f"assistant may not open arena: {hint['hint_id']}")
        require("become_contestant" not in hint.get("assistant_allowed", []), f"assistant may not become contestant: {hint['hint_id']}")

        for move in hint["recommended_lawful_moves"]:
            require(move in lawful_moves, f"unknown lawful move {move} in {hint['hint_id']}")

        forbidden_text = json.dumps(hint, ensure_ascii=False).lower()
        for forbidden in FORBIDDEN_HINT_FIELDS:
            require(forbidden not in hint.keys(), f"forbidden hint field present: {forbidden}")
        for right in FORBIDDEN_ASSISTANT_RIGHTS:
            require(right not in hint.get("assistant_allowed", []), f"assistant forbidden right leaked: {right}")

    stop_lines = set(registry["stop_lines"])
    for expected in [
        "no_arena_session_creation",
        "no_verdict",
        "no_scar_write",
        "no_retention_scheduling",
        "no_rank_mutation",
        "no_tos_promotion",
    ]:
        require(expected in stop_lines, f"missing stop-line: {expected}")

    for report in optional_dependency_report():
        print(report)
    print("Agon gate routing validation passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
