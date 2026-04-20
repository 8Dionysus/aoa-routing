#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "agon_gate_routing.seed.json"
OUTPUT_PATH = ROOT / "generated" / "agon_gate_routing_registry.min.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_min(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def decision_state_for(action: str) -> str:
    if "quarantine" in action:
        return "quarantine_hint"
    if "missing_context" in action:
        return "agon_gate_candidate_missing_context"
    if "gate_candidate" in action:
        return "agon_gate_candidate"
    if "owner_review" in action:
        return "owner_review_required"
    return "owner_review_required"


def build_registry(config: dict[str, Any]) -> dict[str, Any]:
    route_hints: list[dict[str, Any]] = []

    for trigger in config["triggers"]:
        route_hints.append(
            {
                "hint_id": f"agon_gate.{trigger['trigger_id']}.v1",
                "trigger_id": trigger["trigger_id"],
                "trigger_class": trigger["trigger_class"],
                "routing_action": trigger["routing_action"],
                "decision_state": decision_state_for(trigger["routing_action"]),
                "primary_next_hop": trigger["primary_next_hop"],
                "secondary_next_hops": trigger["secondary_next_hops"],
                "recommended_lawful_moves": trigger["recommended_lawful_moves"],
                "assistant_allowed": trigger["assistant_allowed"],
                "assistant_forbidden": trigger["assistant_forbidden"],
                "live_protocol": False,
                "runtime_effect": "none",
                "routing_owns": ["thin pre-protocol gate hint", "next-hop orientation"],
                "routing_must_not_own": config["stop_lines"],
            }
        )

    return {
        "schema_version": "agon_gate_routing_registry.v1",
        "wave": config["wave"],
        "status": config["status"],
        "owner_repo": config["owner_repo"],
        "center_repo": config["center_repo"],
        "source_authority_refs": config["source_authority_refs"],
        "decision_states": config["decision_states"],
        "stop_lines": config["stop_lines"],
        "trigger_count": len(config["triggers"]),
        "route_hint_count": len(route_hints),
        "trigger_classes": sorted({trigger["trigger_class"] for trigger in config["triggers"]}),
        "triggers": config["triggers"],
        "route_hints": route_hints,
        "validation_invariants": [
            "all route hints are pre-protocol",
            "no route hint may open an arena session",
            "no assistant route may grant arena authority",
            "routing emits candidates and next-hop orientation only",
            "center-owned Agon law remains outside aoa-routing",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Agon gate routing registry.")
    parser.add_argument("--check", action="store_true", help="Fail if generated output is stale.")
    args = parser.parse_args()

    config = load_json(CONFIG_PATH)
    registry = build_registry(config)
    rendered = dump_min(registry)

    if args.check:
        if not OUTPUT_PATH.exists():
            raise SystemExit(f"Missing generated output: {OUTPUT_PATH}")
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit("generated/agon_gate_routing_registry.min.json is stale")
        print("Agon gate routing registry is up to date.")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
