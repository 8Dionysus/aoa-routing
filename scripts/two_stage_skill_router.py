#!/usr/bin/env python3
"""Runtime helper for the wave-9 two-stage skill router."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _wave9_router_lib import build_decision_packet, load_json, preselect


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the wave-9 two-stage skill router.")
    parser.add_argument("command", choices=["preselect", "decision-packet", "route"])
    parser.add_argument("--routing-root", default=".", type=Path, help="aoa-routing repository root.")
    parser.add_argument("--skills-root", default=Path("..") / "aoa-skills", type=Path, help="aoa-skills repository root.")
    parser.add_argument("--task", required=True, help="Task text to route.")
    parser.add_argument("--repo-family", default=None, help="Optional repo family hint such as atm10.")
    parser.add_argument("--top-k", type=int, default=None, help="Override shortlist size.")
    parser.add_argument("--shortlist", nargs="*", default=[], help="Shortlist names for decision-packet mode.")
    parser.add_argument("--format", choices=["json"], default="json")
    args = parser.parse_args()

    routing_root = args.routing_root.resolve()
    skills_root = args.skills_root.resolve()
    policy = load_json(routing_root / "config" / "two_stage_router_policy.json")
    signals = load_json(skills_root / "generated" / "tiny_router_skill_signals.json")
    bands = load_json(skills_root / "generated" / "tiny_router_candidate_bands.json")

    if args.command == "preselect":
        print_json(preselect(args.task, signals, bands, policy, top_k=args.top_k, repo_family=args.repo_family))
        return 0

    if args.command == "decision-packet":
        preselect_payload = {
            "task": args.task,
            "repo_family": args.repo_family,
            "top_bands": [],
            "shortlist": [{"name": name} for name in args.shortlist],
            "confidence": "strong" if args.shortlist else "empty",
            "lead_score": None,
            "lead_gap": None,
            "fallback_candidates": [],
        }
        print_json(build_decision_packet(args.task, preselect_payload, skills_root))
        return 0

    preselected = preselect(args.task, signals, bands, policy, top_k=args.top_k, repo_family=args.repo_family)
    packet = build_decision_packet(args.task, preselected, skills_root)
    print_json({"preselect": preselected, "decision_packet": packet})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
