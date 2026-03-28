#!/usr/bin/env python3
"""Build wave-9 two-stage skill-routing artifacts for aoa-routing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _wave9_router_lib import build_decision_packet, load_json, load_jsonl, preselect


PROFILE = "aoa-routing-wave-9-two-stage-skill-router"
JSON_INDENT = 2


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=JSON_INDENT, ensure_ascii=False) + "\n"


def render_or_check(path: Path, text: str, check: bool, repo_root: Path) -> None:
    if check:
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != text:
            raise SystemExit(f"{path.relative_to(repo_root).as_posix()} is out of date")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_outputs(
    *,
    routing_root: Path,
    skills_root: Path,
    tiny_model_entrypoints: dict[str, Any],
    aoa_router: dict[str, Any],
    pairing_hints: dict[str, Any],
    task_to_surface_hints: dict[str, Any],
) -> dict[str, dict[str, Any] | list[dict[str, Any]]]:
    generated_dir = skills_root / "generated"
    policy = load_json(routing_root / "config" / "two_stage_router_policy.json")
    tiny_capsules = load_json(generated_dir / "tiny_router_capsules.min.json")
    tiny_bands = load_json(generated_dir / "tiny_router_candidate_bands.json")
    tiny_signals = load_json(generated_dir / "tiny_router_skill_signals.json")
    tiny_eval_cases = load_jsonl(generated_dir / "tiny_router_eval_cases.jsonl")

    entrypoints = {
        "schema_version": 1,
        "profile": PROFILE,
        "inherits_from": policy["defaults"]["existing_tiny_entrypoints_ref"],
        "stage_1": {
            "name": "tiny-skill-preselector",
            "source_repo": "aoa-skills",
            "target_surface": "generated/tiny_router_capsules.min.json",
            "bands_surface": "generated/tiny_router_candidate_bands.json",
            "signals_surface": "generated/tiny_router_skill_signals.json",
            "top_k_default": policy["defaults"]["top_k"],
            "activation_policy": "never-activate",
            "manual_policy": "include-but-mark-manual",
            "policy_ref": "config/two_stage_router_policy.json",
        },
        "stage_2": {
            "name": "main-model-skill-decider",
            "source_repo": "aoa-skills",
            "shortlist_surface": "generated/skill_capsules.json",
            "activation_manifest": "generated/local_adapter_manifest.json",
            "context_manifest": "generated/context_retention_manifest.json",
            "decision_modes": policy["defaults"]["decision_modes"],
        },
        "starters": [
            {
                "name": "skill-preselect",
                "verb": "preselect",
                "source_repo": "aoa-skills",
                "target_surface": "generated/tiny_router_capsules.min.json",
                "top_k": policy["defaults"]["top_k"],
            },
            {
                "name": "skill-preselect-risk",
                "verb": "preselect",
                "source_repo": "aoa-skills",
                "target_surface": "generated/tiny_router_capsules.min.json",
                "band_hint": "risk-ops-safety",
                "top_k": policy["defaults"]["top_k"],
            },
            {
                "name": "skill-preselect-overlay",
                "verb": "preselect",
                "source_repo": "aoa-skills",
                "target_surface": "generated/tiny_router_capsules.min.json",
                "repo_family": "atm10",
                "top_k": policy["defaults"]["top_k"],
            },
            {
                "name": "skill-decision-packet",
                "verb": "decision-packet",
                "source_repo": "aoa-skills",
                "target_surface": "generated/skill_capsules.json",
                "activation_manifest": "generated/local_adapter_manifest.json",
            },
        ],
        "routing_refs": {
            "tiny_model_entrypoints": "generated/tiny_model_entrypoints.json",
            "aoa_router": "generated/aoa_router.min.json",
            "pairing_hints": "generated/pairing_hints.min.json",
            "task_to_surface_hints": "generated/task_to_surface_hints.json",
        },
    }

    prompt_blocks = {
        "schema_version": 1,
        "profile": PROFILE,
        "tiny_preselector_system": (
            "You are a tiny skill preselector. Read only compressed skill cards, "
            "candidate bands, and their cues. Never activate a skill. Return at most "
            "three positive-signal candidate names, confidence metadata, and any "
            "out-of-band fallback visibility. Never treat fallback candidates as the live shortlist."
        ),
        "main_model_decision_system": (
            "You are the stage-2 skill decider. Read only the shortlist packet and "
            "the full capsules for shortlisted skills. Choose at most one skill or no "
            "skill. Weak or empty shortlists must stay no-skill. Explicit-only skills must stay manual."
        ),
        "handoff_contract": [
            "stage 1 narrows the candidate set",
            "stage 1 never activates a skill",
            "stage 2 may activate one candidate, require a manual handle, or choose no skill",
            "explicit-only skills stay manual even when they win stage 1",
            "fallback candidates stay out-of-band and do not replace the shortlist",
            "weak or empty shortlists must end in no-skill",
        ],
    }

    tool_schemas = {
        "schema_version": 1,
        "profile": PROFILE,
        "tools": [
            {
                "name": "preselect_skills",
                "description": "Return a top-3 positive-signal skill shortlist plus confidence metadata from compressed tiny-router cards.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "repo_family": {"type": "string"},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    "required": ["task"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "build_skill_decision_packet",
                "description": "Build the stage-2 shortlist packet for the main model.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "shortlist_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "maxItems": 5,
                        },
                    },
                    "required": ["task", "shortlist_names"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "route_skill_task",
                "description": "Run stage-1 preselection and return a precision-first stage-2 decision packet.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "repo_family": {"type": "string"},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    "required": ["task"],
                    "additionalProperties": False,
                },
            },
        ],
    }

    examples: list[dict[str, Any]] = []
    routing_eval_cases: list[dict[str, Any]] = []
    for case in tiny_eval_cases:
        preselected = preselect(
            task=case["prompt"],
            signals_doc=tiny_signals,
            bands_doc=tiny_bands,
            policy=policy,
            top_k=policy["defaults"]["top_k"],
            repo_family=case.get("repo_family_hint"),
        )
        packet = build_decision_packet(case["prompt"], preselected, skills_root)
        if len(examples) < 8:
            examples.append(
                {
                    "case_id": case["case_id"],
                    "prompt": case["prompt"],
                    "preselect_result": preselected,
                    "decision_packet": packet,
                }
            )

        top_band = preselected["top_bands"][0]["id"] if preselected.get("top_bands") else None
        routing_eval_cases.append(
            {
                "case_id": case["case_id"],
                "prompt": case["prompt"],
                "repo_family_hint": case.get("repo_family_hint"),
                "expected_shortlist_includes": case.get("expected_shortlist_includes", []),
                "expected_shortlist_excludes": case.get("expected_shortlist_excludes", []),
                "expected_top1": case.get("expected_top1"),
                "expected_top1_not": case.get("expected_top1_not"),
                "expected_band": top_band,
                "stage_2_expectation": packet["suggested_decision"]["decision_mode"],
            }
        )

    manifest = {
        "schema_version": 1,
        "profile": PROFILE,
        "policy_ref": "config/two_stage_router_policy.json",
        "integration_mode": "adjacent-seam",
        "source_inputs": [
            "generated/tiny_model_entrypoints.json",
            "generated/aoa_router.min.json",
            "generated/pairing_hints.min.json",
            "generated/task_to_surface_hints.json",
            "../aoa-skills/generated/tiny_router_capsules.min.json",
            "../aoa-skills/generated/tiny_router_candidate_bands.json",
            "../aoa-skills/generated/tiny_router_skill_signals.json",
            "../aoa-skills/generated/skill_capsules.json",
            "../aoa-skills/generated/local_adapter_manifest.json",
            "../aoa-skills/generated/context_retention_manifest.json",
        ],
        "skill_count": len(tiny_capsules.get("skills", [])),
        "band_count": len(tiny_bands.get("bands", [])),
        "example_count": len(examples),
        "eval_case_count": len(routing_eval_cases),
        "base_entrypoint_count": len(tiny_model_entrypoints.get("starters", [])),
        "router_skill_entry_count": len([entry for entry in aoa_router.get("entries", []) if entry.get("kind") == "skill"]),
        "pairing_entry_count": len(pairing_hints.get("entries", [])),
        "task_hint_kinds": [entry["kind"] for entry in task_to_surface_hints.get("hints", [])],
    }

    return {
        "two_stage_skill_entrypoints.json": entrypoints,
        "two_stage_router_prompt_blocks.json": prompt_blocks,
        "two_stage_router_tool_schemas.json": tool_schemas,
        "two_stage_router_examples.json": {
            "schema_version": 1,
            "profile": PROFILE,
            "examples": examples,
        },
        "two_stage_router_manifest.json": manifest,
        "two_stage_router_eval_cases.jsonl": routing_eval_cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build wave-9 two-stage skill-routing surfaces.")
    parser.add_argument("--routing-root", default=".", type=Path, help="aoa-routing repository root.")
    parser.add_argument("--skills-root", default=Path("..") / "aoa-skills", type=Path, help="aoa-skills repository root.")
    parser.add_argument("--check", action="store_true", help="Check whether generated outputs are current.")
    args = parser.parse_args()

    routing_root = args.routing_root.resolve()
    generated_dir = routing_root / "generated"
    outputs = build_outputs(
        routing_root=routing_root,
        skills_root=args.skills_root.resolve(),
        tiny_model_entrypoints=load_json(generated_dir / "tiny_model_entrypoints.json"),
        aoa_router=load_json(generated_dir / "aoa_router.min.json"),
        pairing_hints=load_json(generated_dir / "pairing_hints.min.json"),
        task_to_surface_hints=load_json(generated_dir / "task_to_surface_hints.json"),
    )

    for filename, payload in outputs.items():
        text = dump_json(payload) if not filename.endswith(".jsonl") else "".join(
            json.dumps(row, ensure_ascii=False) + "\n" for row in payload
        )
        render_or_check(generated_dir / filename, text, args.check, routing_root)
    print(json.dumps({"status": "ok", "routing_root": str(routing_root), "check": args.check}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
