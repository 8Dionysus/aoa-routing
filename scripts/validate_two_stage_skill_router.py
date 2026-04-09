#!/usr/bin/env python3
"""Validate wave-9 two-stage skill-routing artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _wave9_router_lib import (
    build_decision_packet,
    load_json,
    load_jsonl,
    preselect,
    resolve_stage_2_shortlist_limit,
)


PROFILE = "aoa-routing-wave-9-two-stage-skill-router"
LOCAL_PRECISION_CASES_PATH = Path("config") / "two_stage_router_precision_cases.jsonl"
VALIDATION_REFS = [
    "scripts/build_two_stage_skill_router.py",
    "scripts/validate_two_stage_skill_router.py",
    "tests/test_two_stage_skill_router.py",
]
FORBIDDEN_EXAMPLE_CANDIDATE_FIELDS = {
    "summary",
    "trigger_boundary_short",
    "verification_short",
    "allowlist_paths",
    "context_rehydration_hint",
    "companions",
}


def resolve_generated_dir(path: Path) -> Path:
    if (path / "two_stage_skill_entrypoints.json").exists():
        return path
    candidate = path / "generated"
    if (candidate / "two_stage_skill_entrypoints.json").exists():
        return candidate
    return path


def resolve_routing_root(path: Path) -> tuple[Path, bool]:
    resolved = path.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / "config" / "two_stage_router_policy.json").exists():
            return candidate, False
    return Path(__file__).resolve().parents[1], True


def load_optional_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return load_jsonl(path)


def add_behavior_issue(
    issues: list[tuple[str, str]],
    *,
    source_label: str,
    case_id: str,
    field: str,
    message: str,
) -> None:
    issues.append((f"{source_label}:{case_id}:{field}", message))


def validate_behavior_case(
    *,
    case: dict[str, Any],
    preselected: dict[str, Any],
    packet: dict[str, Any],
    issues: list[tuple[str, str]],
    source_label: str,
) -> None:
    case_id = case.get("case_id", "unknown-case")
    shortlist_names = [entry.get("name") for entry in preselected.get("shortlist", []) if entry.get("name")]
    top1 = shortlist_names[0] if shortlist_names else None
    top_band = None
    if preselected.get("top_bands"):
        top_band = preselected["top_bands"][0].get("id")
    decision_mode = packet.get("suggested_decision", {}).get("decision_mode")

    for name in case.get("expected_shortlist_includes", []):
        if name not in shortlist_names:
            add_behavior_issue(
                issues,
                source_label=source_label,
                case_id=case_id,
                field="expected_shortlist_includes",
                message=f"expected shortlist to include {name!r}, got {shortlist_names!r}",
            )
    for name in case.get("expected_shortlist_excludes", []):
        if name in shortlist_names:
            add_behavior_issue(
                issues,
                source_label=source_label,
                case_id=case_id,
                field="expected_shortlist_excludes",
                message=f"expected shortlist to exclude {name!r}, got {shortlist_names!r}",
            )

    expected_top1 = case.get("expected_top1")
    if expected_top1 is not None and top1 != expected_top1:
        add_behavior_issue(
            issues,
            source_label=source_label,
            case_id=case_id,
            field="expected_top1",
            message=f"expected top1 {expected_top1!r}, got {top1!r}",
        )

    expected_top1_not = case.get("expected_top1_not")
    if expected_top1_not is not None and top1 == expected_top1_not:
        add_behavior_issue(
            issues,
            source_label=source_label,
            case_id=case_id,
            field="expected_top1_not",
            message=f"expected top1 to differ from {expected_top1_not!r}",
        )

    expected_band = case.get("expected_band")
    if expected_band is not None and top_band != expected_band:
        add_behavior_issue(
            issues,
            source_label=source_label,
            case_id=case_id,
            field="expected_band",
            message=f"expected top band {expected_band!r}, got {top_band!r}",
        )

    expected_confidence = case.get("expected_confidence")
    if expected_confidence is not None and preselected.get("confidence") != expected_confidence:
        add_behavior_issue(
            issues,
            source_label=source_label,
            case_id=case_id,
            field="expected_confidence",
            message=f"expected confidence {expected_confidence!r}, got {preselected.get('confidence')!r}",
        )

    if "expect_fallback_candidates" in case:
        expected_fallback_visibility = bool(case["expect_fallback_candidates"])
        actual_fallback_visibility = bool(preselected.get("fallback_candidates"))
        if actual_fallback_visibility != expected_fallback_visibility:
            add_behavior_issue(
                issues,
                source_label=source_label,
                case_id=case_id,
                field="expect_fallback_candidates",
                message=(
                    f"expected fallback visibility {expected_fallback_visibility!r}, "
                    f"got {actual_fallback_visibility!r}"
                ),
            )

    expected_stage_2 = case.get("stage_2_expectation")
    if expected_stage_2 is not None and decision_mode != expected_stage_2:
        add_behavior_issue(
            issues,
            source_label=source_label,
            case_id=case_id,
            field="stage_2_expectation",
            message=f"expected stage-2 decision {expected_stage_2!r}, got {decision_mode!r}",
        )


def validate_outputs(routing_root: Path, skills_root: Path) -> list[tuple[str, str]]:
    generated_dir = resolve_generated_dir(routing_root)
    routing_root, used_fallback_root = resolve_routing_root(routing_root)
    issues: list[tuple[str, str]] = []
    entrypoints = load_json(generated_dir / "two_stage_skill_entrypoints.json")
    prompt_blocks = load_json(generated_dir / "two_stage_router_prompt_blocks.json")
    tool_schemas = load_json(generated_dir / "two_stage_router_tool_schemas.json")
    examples = load_json(generated_dir / "two_stage_router_examples.json")
    manifest = load_json(generated_dir / "two_stage_router_manifest.json")
    eval_cases = load_jsonl(generated_dir / "two_stage_router_eval_cases.jsonl")
    local_precision_cases = []
    if not used_fallback_root:
        local_precision_cases = load_optional_jsonl(routing_root / LOCAL_PRECISION_CASES_PATH)
    tiny_capsules = load_json(skills_root / "generated" / "tiny_router_capsules.min.json")
    tiny_model_entrypoints = load_json(generated_dir / "tiny_model_entrypoints.json")
    policy = load_json(routing_root / "config" / "two_stage_router_policy.json")
    signals = load_json(skills_root / "generated" / "tiny_router_skill_signals.json")
    bands = load_json(skills_root / "generated" / "tiny_router_candidate_bands.json")
    skill_capsules = load_json(skills_root / "generated" / "skill_capsules.json")
    local_adapter_manifest = load_json(skills_root / "generated" / "local_adapter_manifest.json")
    context_retention_manifest = load_json(skills_root / "generated" / "context_retention_manifest.json")
    stage_2_shortlist_limit = resolve_stage_2_shortlist_limit(policy)
    top_k_default = min(int(policy["defaults"]["top_k"]), stage_2_shortlist_limit)
    stage_1_token_budget = int(policy["defaults"]["max_stage_1_tokens"])
    skill_root_starter = policy["defaults"]["skill_root_starter"]

    for label, doc in {
        "two_stage_skill_entrypoints.json": entrypoints,
        "two_stage_router_prompt_blocks.json": prompt_blocks,
        "two_stage_router_tool_schemas.json": tool_schemas,
        "two_stage_router_examples.json": examples,
        "two_stage_router_manifest.json": manifest,
    }.items():
        if doc.get("profile") != PROFILE:
            issues.append((label, f"profile must be {PROFILE!r}"))

    expected_surface_contracts = {
        "two_stage_skill_entrypoints.json": (
            entrypoints,
            "aoa_routing_two_stage_skill_entrypoints_v2",
            "schemas/two-stage-skill-entrypoints.schema.json",
            "two_stage_skill_entrypoints",
        ),
        "two_stage_router_prompt_blocks.json": (
            prompt_blocks,
            "aoa_routing_two_stage_router_prompt_blocks_v2",
            "schemas/two-stage-router-prompt-blocks.schema.json",
            "two_stage_router_prompt_blocks",
        ),
        "two_stage_router_tool_schemas.json": (
            tool_schemas,
            "aoa_routing_two_stage_router_tool_schemas_v2",
            "schemas/two-stage-router-tool-schemas.schema.json",
            "two_stage_router_tool_schemas",
        ),
        "two_stage_router_examples.json": (
            examples,
            "aoa_routing_two_stage_router_examples_v2",
            "schemas/two-stage-router-examples.schema.json",
            "two_stage_router_examples",
        ),
        "two_stage_router_manifest.json": (
            manifest,
            "aoa_routing_two_stage_router_manifest_v2",
            "schemas/two-stage-router-manifest.schema.json",
            "two_stage_router_manifest",
        ),
    }
    for label, (doc, schema_version, schema_ref, surface_kind) in expected_surface_contracts.items():
        if doc.get("schema_version") != schema_version:
            issues.append((label, f"schema_version must stay {schema_version!r}"))
        if doc.get("schema_ref") != schema_ref:
            issues.append((label, f"schema_ref must stay {schema_ref!r}"))
        if doc.get("owner_repo") != "aoa-routing":
            issues.append((label, "owner_repo must stay 'aoa-routing'"))
        if doc.get("surface_kind") != surface_kind:
            issues.append((label, f"surface_kind must stay {surface_kind!r}"))
        if doc.get("validation_refs") != VALIDATION_REFS:
            issues.append((label, "validation_refs mismatch"))

    skill_names = {entry["name"] for entry in tiny_capsules.get("skills", [])}
    top_k_default_payload = entrypoints.get("stage_1", {}).get("top_k_default")
    if entrypoints.get("stage_1", {}).get("activation_policy") != "never-activate":
        issues.append(("two_stage_skill_entrypoints.json", "stage_1 activation_policy must stay never-activate"))
    if entrypoints.get("stage_2", {}).get("decision_modes") != [
        "activate-candidate",
        "manual-invocation-required",
        "no-skill",
    ]:
        issues.append(("two_stage_skill_entrypoints.json", "stage_2 decision_modes mismatch"))
    if entrypoints.get("routing_refs", {}).get("tiny_model_entrypoints") != "generated/tiny_model_entrypoints.json":
        issues.append(("two_stage_skill_entrypoints.json", "routing_refs tiny_model_entrypoints mismatch"))
    if policy.get("defaults", {}).get("fallback_visibility_mode") != "out_of_band_only":
        issues.append(("config/two_stage_router_policy.json", "fallback_visibility_mode must stay 'out_of_band_only'"))
    if entrypoints.get("inherits_from") != policy["defaults"]["existing_tiny_entrypoints_ref"]:
        issues.append(("two_stage_skill_entrypoints.json", "inherits_from mismatch"))
    if top_k_default_payload != top_k_default:
        issues.append(("two_stage_skill_entrypoints.json", "stage_1 top_k_default must honor the configured shortlist cap"))
    if entrypoints.get("stage_1", {}).get("starter_ref") != skill_root_starter:
        issues.append(("two_stage_skill_entrypoints.json", "stage_1 starter_ref mismatch"))
    if entrypoints.get("stage_1", {}).get("max_stage_1_tokens") != stage_1_token_budget:
        issues.append(("two_stage_skill_entrypoints.json", "stage_1 max_stage_1_tokens mismatch"))
    if entrypoints.get("stage_2", {}).get("max_shortlist") != stage_2_shortlist_limit:
        issues.append(("two_stage_skill_entrypoints.json", "stage_2 max_shortlist mismatch"))
    starters = tiny_model_entrypoints.get("starters", [])
    starter_names = {entry.get("name") for entry in starters}
    if skill_root_starter not in starter_names:
        issues.append(("tiny_model_entrypoints.json", f"missing starter {skill_root_starter!r} required by wave-9 policy"))
    skill_root_entry = next(
        (
            entry
            for entry in starters
            if entry.get("name") == skill_root_starter
        ),
        None,
    )
    if skill_root_entry is not None:
        if skill_root_entry.get("verb") != "pick":
            issues.append(("tiny_model_entrypoints.json", f"starter {skill_root_starter!r} must stay a pick starter"))
        if skill_root_entry.get("source_repo") != "aoa-routing":
            issues.append(("tiny_model_entrypoints.json", f"starter {skill_root_starter!r} must stay on aoa-routing"))
        if skill_root_entry.get("target_surface") != "generated/aoa_router.min.json":
            issues.append(
                (
                    "tiny_model_entrypoints.json",
                    f"starter {skill_root_starter!r} must target generated/aoa_router.min.json",
                )
            )
        if skill_root_entry.get("allowed_kinds") != ["skill"]:
            issues.append(
                (
                    "tiny_model_entrypoints.json",
                    f"starter {skill_root_starter!r} must stay skill-only",
                )
            )
        if skill_root_entry.get("target_kind") != "skill" or skill_root_entry.get("target_value") != "skill":
            issues.append(
                (
                    "tiny_model_entrypoints.json",
                    f"starter {skill_root_starter!r} must keep target_kind/target_value pinned to 'skill'",
                )
            )
    if entrypoints.get("stage_1", {}).get("source_repo") != "aoa-skills":
        issues.append(("two_stage_skill_entrypoints.json", "stage_1 source_repo must stay aoa-skills"))
    if entrypoints.get("stage_2", {}).get("source_repo") != "aoa-skills":
        issues.append(("two_stage_skill_entrypoints.json", "stage_2 source_repo must stay aoa-skills"))
    tiny_model_handoff = entrypoints.get("tiny_model_handoff", {})
    if not isinstance(tiny_model_handoff, dict):
        issues.append(("two_stage_skill_entrypoints.json", "tiny_model_handoff must be a mapping"))
        tiny_model_handoff = {}
    if tiny_model_handoff.get("starter_ref") != skill_root_starter:
        issues.append(("two_stage_skill_entrypoints.json", "tiny_model_handoff starter_ref mismatch"))
    if tiny_model_handoff.get("entry_surface") != policy["defaults"]["existing_tiny_entrypoints_ref"]:
        issues.append(("two_stage_skill_entrypoints.json", "tiny_model_handoff entry_surface mismatch"))
    if tiny_model_handoff.get("handoff_name") != "two-stage-skill-selection":
        issues.append(("two_stage_skill_entrypoints.json", "tiny_model_handoff handoff_name mismatch"))
    if tiny_model_handoff.get("handoff_mode") != "optional-adjacent":
        issues.append(("two_stage_skill_entrypoints.json", "tiny_model_handoff handoff_mode mismatch"))
    if tiny_model_handoff.get("activation_authority") != "source-owned":
        issues.append(("two_stage_skill_entrypoints.json", "tiny_model_handoff activation_authority mismatch"))
    skill_root_handoff = {}
    if isinstance(skill_root_entry, dict):
        raw_skill_root_handoff = skill_root_entry.get("adjacent_handoff", {})
        if not isinstance(raw_skill_root_handoff, dict):
            issues.append(("tiny_model_entrypoints.json", "skill-root adjacent_handoff must be a mapping"))
        else:
            skill_root_handoff = raw_skill_root_handoff
    if skill_root_entry is not None and not skill_root_handoff:
        issues.append(("tiny_model_entrypoints.json", "skill-root must publish an explicit adjacent_handoff into the two-stage seam"))
    if skill_root_handoff.get("name") != "two-stage-skill-selection":
        issues.append(("tiny_model_entrypoints.json", "skill-root adjacent_handoff name mismatch"))
    if skill_root_handoff.get("target_repo") != "aoa-routing":
        issues.append(("tiny_model_entrypoints.json", "skill-root adjacent_handoff target_repo mismatch"))
    if skill_root_handoff.get("target_surface") != "generated/two_stage_skill_entrypoints.json":
        issues.append(("tiny_model_entrypoints.json", "skill-root adjacent_handoff target_surface mismatch"))
    if skill_root_handoff.get("surface_kind") != "two_stage_skill_entrypoints":
        issues.append(("tiny_model_entrypoints.json", "skill-root adjacent_handoff surface_kind mismatch"))
    if skill_root_handoff.get("handoff_mode") != "optional-adjacent":
        issues.append(("tiny_model_entrypoints.json", "skill-root adjacent_handoff handoff_mode mismatch"))
    if skill_root_handoff.get("activation_authority") != "source-owned":
        issues.append(("tiny_model_entrypoints.json", "skill-root adjacent_handoff activation_authority mismatch"))
    if not isinstance(skill_root_handoff.get("when"), str) or not skill_root_handoff.get("when", "").strip():
        issues.append(("tiny_model_entrypoints.json", "skill-root adjacent_handoff when must stay non-empty"))
    if entrypoints.get("stage_2", {}).get("activation_manifest") != "generated/local_adapter_manifest.json":
        issues.append(("two_stage_skill_entrypoints.json", "stage_2 activation_manifest mismatch"))
    if entrypoints.get("stage_2", {}).get("context_manifest") != "generated/context_retention_manifest.json":
        issues.append(("two_stage_skill_entrypoints.json", "stage_2 context_manifest mismatch"))
    stage_2_surface_sets = {
        "skill_capsules.json": {entry["name"] for entry in skill_capsules.get("skills", [])},
        "local_adapter_manifest.json": {entry["name"] for entry in local_adapter_manifest.get("skills", [])},
        "context_retention_manifest.json": {entry["name"] for entry in context_retention_manifest.get("skills", [])},
    }
    for label, surface_names in stage_2_surface_sets.items():
        if surface_names != skill_names:
            missing = sorted(skill_names - surface_names)
            extra = sorted(surface_names - skill_names)
            parts: list[str] = []
            if missing:
                parts.append(f"missing {missing!r}")
            if extra:
                parts.append(f"unexpected {extra!r}")
            issues.append((label, f"stage-2 surface coverage mismatch: {'; '.join(parts)}"))
    for entry in local_adapter_manifest.get("skills", []):
        allowlist_paths = entry.get("allowlist_paths")
        if not isinstance(allowlist_paths, list) or not allowlist_paths:
            issues.append(("local_adapter_manifest.json", f"skill {entry.get('name')!r} must keep a non-empty allowlist_paths"))
    for entry in skill_capsules.get("skills", []):
        skill_path = entry.get("skill_path")
        if not isinstance(skill_path, str) or not skill_path:
            issues.append(("skill_capsules.json", f"skill {entry.get('name')!r} must keep a source-owned skill_path"))

    preselect_tool = next((tool for tool in tool_schemas.get("tools", []) if tool.get("name") == "preselect_skills"), None)
    decision_packet_tool = next(
        (tool for tool in tool_schemas.get("tools", []) if tool.get("name") == "build_skill_decision_packet"),
        None,
    )
    route_tool = next((tool for tool in tool_schemas.get("tools", []) if tool.get("name") == "route_skill_task"), None)

    if len(tool_schemas.get("tools", [])) != 3:
        issues.append(("two_stage_router_tool_schemas.json", "expected exactly 3 tool schemas"))
    if "tiny_preselector_system" not in prompt_blocks or "main_model_decision_system" not in prompt_blocks:
        issues.append(("two_stage_router_prompt_blocks.json", "missing required prompt blocks"))
    if prompt_blocks.get("policy_ref") != "config/two_stage_router_policy.json":
        issues.append(("two_stage_router_prompt_blocks.json", "policy_ref mismatch"))
    if prompt_blocks.get("stage_1_token_budget") != stage_1_token_budget:
        issues.append(("two_stage_router_prompt_blocks.json", "stage_1_token_budget mismatch"))
    if prompt_blocks.get("stage_2_shortlist_limit") != stage_2_shortlist_limit:
        issues.append(("two_stage_router_prompt_blocks.json", "stage_2_shortlist_limit mismatch"))
    if tool_schemas.get("policy_ref") != "config/two_stage_router_policy.json":
        issues.append(("two_stage_router_tool_schemas.json", "policy_ref mismatch"))
    if tool_schemas.get("stage_2_shortlist_limit") != stage_2_shortlist_limit:
        issues.append(("two_stage_router_tool_schemas.json", "stage_2_shortlist_limit mismatch"))
    if preselect_tool is not None:
        preselect_top_k_max = (
            preselect_tool.get("input_schema", {})
            .get("properties", {})
            .get("top_k", {})
            .get("maximum")
        )
        if preselect_top_k_max != stage_2_shortlist_limit:
            issues.append(("two_stage_router_tool_schemas.json", "preselect top_k maximum mismatch"))
    if route_tool is not None:
        route_top_k_max = (
            route_tool.get("input_schema", {})
            .get("properties", {})
            .get("top_k", {})
            .get("maximum")
        )
        if route_top_k_max != stage_2_shortlist_limit:
            issues.append(("two_stage_router_tool_schemas.json", "route top_k maximum mismatch"))
    if decision_packet_tool is not None:
        shortlist_max = (
            decision_packet_tool.get("input_schema", {})
            .get("properties", {})
            .get("shortlist_names", {})
            .get("maxItems")
        )
        if shortlist_max != stage_2_shortlist_limit:
            issues.append(("two_stage_router_tool_schemas.json", "decision-packet shortlist limit mismatch"))

    for example in examples.get("examples", []):
        shortlist = example.get("preselect_result", {}).get("shortlist", [])
        if top_k_default_payload is not None and len(shortlist) > top_k_default_payload:
            issues.append(("two_stage_router_examples.json", "example shortlist exceeds configured top_k"))
        for item in shortlist:
            if item.get("name") not in skill_names:
                issues.append(("two_stage_router_examples.json", f"unknown skill in shortlist: {item.get('name')!r}"))
        decision_packet = example.get("decision_packet", {})
        projected_candidates = decision_packet.get("candidates", [])
        if decision_packet.get("candidate_count") != len(projected_candidates):
            issues.append(("two_stage_router_examples.json", "example candidate_count mismatch"))
        for item in projected_candidates:
            if item.get("name") not in skill_names:
                issues.append(("two_stage_router_examples.json", f"unknown skill in decision packet: {item.get('name')!r}"))
            forbidden_fields = sorted(FORBIDDEN_EXAMPLE_CANDIDATE_FIELDS.intersection(item))
            if forbidden_fields:
                issues.append(
                    (
                        "two_stage_router_examples.json",
                        f"example decision packet duplicates source-owned capsule fields: {', '.join(forbidden_fields)}",
                    )
                )

    for case in eval_cases:
        for name in case.get("expected_shortlist_includes", []):
            if name not in skill_names:
                issues.append(("two_stage_router_eval_cases.jsonl", f"unknown expected skill {name!r}"))
        top1 = case.get("expected_top1")
        if top1 is not None and top1 not in skill_names:
            issues.append(("two_stage_router_eval_cases.jsonl", f"unknown expected_top1 {top1!r}"))
        top1_not = case.get("expected_top1_not")
        if top1_not is not None and top1_not not in skill_names:
            issues.append(("two_stage_router_eval_cases.jsonl", f"unknown expected_top1_not {top1_not!r}"))

    if manifest.get("skill_count") != len(skill_names):
        issues.append(("two_stage_router_manifest.json", "skill_count mismatch"))
    if manifest.get("example_count") != len(examples.get("examples", [])):
        issues.append(("two_stage_router_manifest.json", "example_count mismatch"))
    if manifest.get("eval_case_count") != len(eval_cases):
        issues.append(("two_stage_router_manifest.json", "eval_case_count mismatch"))
    if manifest.get("integration_mode") != "adjacent-seam":
        issues.append(("two_stage_router_manifest.json", "integration_mode mismatch"))
    if manifest.get("policy_ref") != "config/two_stage_router_policy.json":
        issues.append(("two_stage_router_manifest.json", "policy_ref mismatch"))
    if manifest.get("stage_1_token_budget") != stage_1_token_budget:
        issues.append(("two_stage_router_manifest.json", "stage_1_token_budget mismatch"))
    if manifest.get("stage_2_shortlist_limit") != stage_2_shortlist_limit:
        issues.append(("two_stage_router_manifest.json", "stage_2_shortlist_limit mismatch"))
    if manifest.get("skill_root_starter") != skill_root_starter:
        issues.append(("two_stage_router_manifest.json", "skill_root_starter mismatch"))

    for case in eval_cases:
        preselected = preselect(
            task=case["prompt"],
            signals_doc=signals,
            bands_doc=bands,
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
        validate_behavior_case(
            case=case,
            preselected=preselected,
            packet=packet,
            issues=issues,
            source_label="two_stage_router_eval_cases.jsonl",
        )

    for case in local_precision_cases:
        preselected = preselect(
            task=case["prompt"],
            signals_doc=signals,
            bands_doc=bands,
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
        validate_behavior_case(
            case=case,
            preselected=preselected,
            packet=packet,
            issues=issues,
            source_label=LOCAL_PRECISION_CASES_PATH.as_posix(),
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate wave-9 two-stage skill-routing artifacts.")
    parser.add_argument("--routing-root", default=".", type=Path, help="aoa-routing repository root.")
    parser.add_argument("--skills-root", default=Path("..") / "aoa-skills", type=Path, help="aoa-skills repository root.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print output JSON.")
    args = parser.parse_args()

    issues = validate_outputs(args.routing_root.resolve(), args.skills_root.resolve())
    payload = {
        "status": "ok" if not issues else "fail",
        "issues": [{"location": location, "message": message} for location, message in issues],
    }
    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload))
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
