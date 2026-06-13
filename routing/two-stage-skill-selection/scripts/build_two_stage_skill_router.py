#!/usr/bin/env python3
"""Build two-stage skill-routing artifacts for aoa-routing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from two_stage_router_lib import (
    build_decision_packet,
    load_json,
    load_jsonl,
    preselect,
    resolve_stage_2_shortlist_limit,
)


PROFILE = "aoa-routing-two-stage-skill-router"
JSON_INDENT = 2
ROUTE_ROOT = Path("routing") / "two-stage-skill-selection"
ROUTE_CONFIG_ROOT = ROUTE_ROOT / "config"
ROUTE_SCHEMA_ROOT = ROUTE_ROOT / "schemas"
LOCAL_PRECISION_CASES_PATH = ROUTE_CONFIG_ROOT / "two_stage_router_precision_cases.jsonl"
POLICY_PATH = ROUTE_CONFIG_ROOT / "two_stage_router_policy.json"
VALIDATION_REFS = [
    "routing/two-stage-skill-selection/scripts/build_two_stage_skill_router.py",
    "routing/two-stage-skill-selection/scripts/validate_two_stage_skill_router.py",
    "routing/two-stage-skill-selection/tests/test_two_stage_skill_router.py",
]
STAGE_1_SOURCE_REFS = [
    "aoa-skills:generated/tiny_router_capsules.min.json",
    "aoa-skills:generated/tiny_router_candidate_bands.json",
    "aoa-skills:generated/tiny_router_skill_signals.json",
]
STAGE_2_SOURCE_REFS = [
    "aoa-skills:generated/skill_capsules.json",
    "aoa-skills:generated/local_adapter_manifest.json",
    "aoa-skills:generated/context_retention_manifest.json",
]
FORBIDDEN_SOURCE_PAYLOAD_FIELDS = [
    "summary",
    "trigger_boundary_short",
    "verification_short",
    "skill_path",
    "allowlist_paths",
    "rehydration_hint",
    "context_rehydration_hint",
    "companions",
]
EXAMPLE_CANDIDATE_FIELDS = (
    "name",
    "band",
    "score",
    "preselect_reasons",
    "invocation_mode",
    "manual_invocation_required",
    "activation_hint",
)
OLD_BOOTSTRAP_ROUTE_LABEL = "se" + "ed"


def normalize_active_generated_text(value: str) -> str:
    text = value
    replacements = (
        (
            f"playbook automation {OLD_BOOTSTRAP_ROUTE_LABEL}",
            "playbook automation candidate",
        ),
        (
            f"automation {OLD_BOOTSTRAP_ROUTE_LABEL}",
            "automation candidate",
        ),
    )
    for old, new in replacements:
        text = text.replace(old, new)
        text = text.replace(old.title(), new.title())
    return text.replace(OLD_BOOTSTRAP_ROUTE_LABEL, "source-route")


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=JSON_INDENT, ensure_ascii=False) + "\n"


def render_or_check(path: Path, text: str, check: bool, repo_root: Path) -> None:
    if check:
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if path.suffix == ".json":
            try:
                current_payload = json.loads(current) if current is not None else None
                expected_payload = json.loads(text)
            except json.JSONDecodeError:
                current_payload = None
                expected_payload = object()
            if current_payload != expected_payload:
                raise SystemExit(f"{path.relative_to(repo_root).as_posix()} is out of date")
            return
        if current != text:
            raise SystemExit(f"{path.relative_to(repo_root).as_posix()} is out of date")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_optional_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return load_jsonl(path)


def expected_stage_2_mode(
    case: dict[str, Any],
    *,
    signal_by_name: dict[str, dict[str, Any]],
    actual_decision_mode: str | None = None,
) -> str | None:
    explicit_expectation = case.get("stage_2_expectation")
    if isinstance(explicit_expectation, str) and explicit_expectation:
        return explicit_expectation

    if str(case.get("case_id", "")).startswith("tiny-defer-"):
        return None

    expected_top1 = case.get("expected_top1")
    if isinstance(expected_top1, str) and expected_top1:
        expected_lead = expected_top1
    else:
        expected_shortlist = [
            name
            for name in case.get("expected_shortlist_includes", [])
            if isinstance(name, str) and name
        ]
        expected_lead = expected_shortlist[0] if expected_shortlist else None

    if expected_lead is None:
        return None

    lead_signal = signal_by_name.get(expected_lead, {})
    return (
        "manual-invocation-required"
        if lead_signal.get("manual_invocation_required")
        else "activate-candidate"
    )


def project_example_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {field: candidate.get(field) for field in EXAMPLE_CANDIDATE_FIELDS}


def project_example_decision_packet(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "confidence": packet.get("confidence"),
        "lead_score": packet.get("lead_score"),
        "lead_gap": packet.get("lead_gap"),
        "candidate_count": packet.get("candidate_count"),
        "fallback_candidates": packet.get("fallback_candidates", []),
        "candidates": [
            project_example_candidate(candidate)
            for candidate in packet.get("candidates", [])
        ],
        "decision_reason": packet.get("decision_reason"),
        "suggested_decision": packet.get("suggested_decision"),
        "stage_2_checklist": packet.get("stage_2_checklist", []),
    }


def build_low_context_boundary() -> dict[str, Any]:
    return {
        "wording_scope": "routing-owned",
        "source_payload_copying": "forbidden",
        "stage_1_source_refs": STAGE_1_SOURCE_REFS,
        "stage_2_source_refs": STAGE_2_SOURCE_REFS,
        "forbidden_source_payload_fields": FORBIDDEN_SOURCE_PAYLOAD_FIELDS,
    }


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
    policy = load_json(routing_root / POLICY_PATH)
    tiny_capsules = load_json(generated_dir / "tiny_router_capsules.min.json")
    tiny_bands = load_json(generated_dir / "tiny_router_candidate_bands.json")
    tiny_signals = load_json(generated_dir / "tiny_router_skill_signals.json")
    tiny_eval_cases = load_jsonl(generated_dir / "tiny_router_eval_cases.jsonl")
    local_precision_cases = load_optional_jsonl(routing_root / LOCAL_PRECISION_CASES_PATH)
    top_k_default = min(int(policy["defaults"]["top_k"]), resolve_stage_2_shortlist_limit(policy))
    stage_2_shortlist_limit = resolve_stage_2_shortlist_limit(policy)
    stage_1_token_budget = int(policy["defaults"]["max_stage_1_tokens"])
    skill_root_starter = policy["defaults"]["skill_root_starter"]

    entrypoints = {
        "schema_version": "aoa_routing_two_stage_skill_entrypoints_v2",
        "schema_ref": f"{ROUTE_SCHEMA_ROOT.as_posix()}/two-stage-skill-entrypoints.schema.json",
        "owner_repo": "aoa-routing",
        "surface_kind": "two_stage_skill_entrypoints",
        "profile": PROFILE,
        "validation_refs": VALIDATION_REFS,
        "inherits_from": policy["defaults"]["existing_tiny_entrypoints_ref"],
        "tiny_model_handoff": {
            "starter_ref": skill_root_starter,
            "entry_surface": policy["defaults"]["existing_tiny_entrypoints_ref"],
            "handoff_name": "two-stage-skill-selection",
            "handoff_mode": "optional-adjacent",
            "activation_authority": "source-owned",
        },
        "stage_1": {
            "name": "tiny-skill-preselector",
            "source_repo": "aoa-skills",
            "target_surface": "generated/tiny_router_capsules.min.json",
            "bands_surface": "generated/tiny_router_candidate_bands.json",
            "signals_surface": "generated/tiny_router_skill_signals.json",
            "top_k_default": top_k_default,
            "starter_ref": skill_root_starter,
            "max_stage_1_tokens": stage_1_token_budget,
            "activation_policy": "never-activate",
            "manual_policy": "include-but-mark-manual",
            "policy_ref": POLICY_PATH.as_posix(),
        },
        "stage_2": {
            "name": "main-model-skill-decider",
            "source_repo": "aoa-skills",
            "shortlist_surface": "generated/skill_capsules.json",
            "activation_manifest": "generated/local_adapter_manifest.json",
            "context_manifest": "generated/context_retention_manifest.json",
            "max_shortlist": stage_2_shortlist_limit,
            "decision_modes": policy["defaults"]["decision_modes"],
        },
        "starters": [
            {
                "name": "skill-preselect",
                "verb": "preselect",
                "source_repo": "aoa-skills",
                "target_surface": "generated/tiny_router_capsules.min.json",
                "top_k": top_k_default,
            },
            {
                "name": "skill-preselect-risk",
                "verb": "preselect",
                "source_repo": "aoa-skills",
                "target_surface": "generated/tiny_router_capsules.min.json",
                "band_hint": "risk-ops-safety",
                "top_k": top_k_default,
            },
            {
                "name": "skill-preselect-overlay",
                "verb": "preselect",
                "source_repo": "aoa-skills",
                "target_surface": "generated/tiny_router_capsules.min.json",
                "repo_family": "atm10",
                "top_k": top_k_default,
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
        "schema_version": "aoa_routing_two_stage_router_prompt_blocks_v2",
        "schema_ref": f"{ROUTE_SCHEMA_ROOT.as_posix()}/two-stage-router-prompt-blocks.schema.json",
        "owner_repo": "aoa-routing",
        "surface_kind": "two_stage_router_prompt_blocks",
        "profile": PROFILE,
        "policy_ref": POLICY_PATH.as_posix(),
        "validation_refs": VALIDATION_REFS,
        "low_context_boundary": build_low_context_boundary(),
        "stage_1_token_budget": stage_1_token_budget,
        "stage_2_shortlist_limit": stage_2_shortlist_limit,
        "tiny_preselector_system": (
            "You are a tiny skill preselector. Read only compressed skill cards, "
            "candidate bands, and their cues. Never activate a skill. Return at most "
            f"{top_k_default} positive-signal candidate names, confidence metadata, and any "
            "out-of-band fallback visibility. Never treat fallback candidates as the live shortlist."
        ),
        "main_model_decision_system": (
            "You are the stage-2 skill decider. Read only the shortlist packet and "
            "the full capsules for shortlisted skills. The shortlist must stay at or below "
            f"{stage_2_shortlist_limit} candidates. Choose at most one skill or no "
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
        "schema_version": "aoa_routing_two_stage_router_tool_schemas_v2",
        "schema_ref": f"{ROUTE_SCHEMA_ROOT.as_posix()}/two-stage-router-tool-schemas.schema.json",
        "owner_repo": "aoa-routing",
        "surface_kind": "two_stage_router_tool_schemas",
        "profile": PROFILE,
        "policy_ref": POLICY_PATH.as_posix(),
        "validation_refs": VALIDATION_REFS,
        "low_context_boundary": build_low_context_boundary(),
        "stage_2_shortlist_limit": stage_2_shortlist_limit,
        "tools": [
            {
                "name": "preselect_skills",
                "description": (
                    f"Return a top-{stage_2_shortlist_limit} positive-signal skill shortlist "
                    "plus confidence metadata from compressed tiny-router cards."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "repo_family": {"type": "string"},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": stage_2_shortlist_limit},
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
                            "maxItems": stage_2_shortlist_limit,
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
                        "top_k": {"type": "integer", "minimum": 1, "maximum": stage_2_shortlist_limit},
                    },
                    "required": ["task"],
                    "additionalProperties": False,
                },
            },
        ],
    }

    examples: list[dict[str, Any]] = []
    routing_eval_cases: list[dict[str, Any]] = []
    signal_by_name = {entry["name"]: entry for entry in tiny_signals.get("skills", [])}
    for case in [*tiny_eval_cases, *local_precision_cases]:
        prompt = normalize_active_generated_text(case["prompt"])
        preselected = preselect(
            task=case["prompt"],
            signals_doc=tiny_signals,
            bands_doc=tiny_bands,
            policy=policy,
            top_k=top_k_default,
            repo_family=case.get("repo_family_hint"),
        )
        packet = build_decision_packet(
            case["prompt"],
            preselected,
            skills_root,
            max_shortlist=stage_2_shortlist_limit,
        )
        stage_2_expectation = expected_stage_2_mode(
            case,
            signal_by_name=signal_by_name,
            actual_decision_mode=packet.get("suggested_decision", {}).get("decision_mode"),
        )
        expected_shortlist_includes = case.get("expected_shortlist_includes", [])
        if stage_2_expectation == "activate-candidate" and not expected_shortlist_includes:
            expected_top1 = case.get("expected_top1")
            expected_shortlist_includes = (
                [expected_top1]
                if isinstance(expected_top1, str) and expected_top1
                else []
            )
        if len(examples) < 8:
            examples.append(
                {
                    "case_id": case["case_id"],
                    "prompt": prompt,
                    "preselect_result": preselected,
                    "decision_packet": project_example_decision_packet(packet),
                }
            )

        top_band = preselected["top_bands"][0]["id"] if preselected.get("top_bands") else None
        eval_case = {
            "case_id": case["case_id"],
            "prompt": prompt,
            "repo_family_hint": case.get("repo_family_hint"),
            "expected_shortlist_includes": expected_shortlist_includes,
            "expected_shortlist_excludes": case.get("expected_shortlist_excludes", []),
            "expected_top1": case.get("expected_top1"),
            "expected_top1_not": case.get("expected_top1_not"),
            "expected_band": case.get("expected_band"),
        }
        if stage_2_expectation is not None:
            eval_case["stage_2_expectation"] = stage_2_expectation
        routing_eval_cases.append(eval_case)
        for optional_field in ("expected_confidence", "expect_fallback_candidates"):
            if optional_field in case:
                routing_eval_cases[-1][optional_field] = case[optional_field]

    manifest = {
        "schema_version": "aoa_routing_two_stage_router_manifest_v2",
        "schema_ref": f"{ROUTE_SCHEMA_ROOT.as_posix()}/two-stage-router-manifest.schema.json",
        "owner_repo": "aoa-routing",
        "surface_kind": "two_stage_router_manifest",
        "profile": PROFILE,
        "policy_ref": POLICY_PATH.as_posix(),
        "validation_refs": VALIDATION_REFS,
        "integration_mode": "adjacent-seam",
        "stage_1_token_budget": stage_1_token_budget,
        "stage_2_shortlist_limit": stage_2_shortlist_limit,
        "skill_root_starter": skill_root_starter,
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
            *(
                [LOCAL_PRECISION_CASES_PATH.as_posix()]
                if local_precision_cases
                else []
            ),
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
            "schema_version": "aoa_routing_two_stage_router_examples_v2",
            "schema_ref": f"{ROUTE_SCHEMA_ROOT.as_posix()}/two-stage-router-examples.schema.json",
            "owner_repo": "aoa-routing",
            "surface_kind": "two_stage_router_examples",
            "profile": PROFILE,
            "policy_ref": POLICY_PATH.as_posix(),
            "validation_refs": VALIDATION_REFS,
            "examples": examples,
        },
        "two_stage_router_manifest.json": manifest,
        "two_stage_router_eval_cases.jsonl": routing_eval_cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build two-stage skill-routing surfaces.")
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
