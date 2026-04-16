#!/usr/bin/env python3
"""Build derived routing surfaces for aoa-routing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_two_stage_skill_router import build_outputs as build_two_stage_outputs
from router_core import (
    CANONICAL_REPO_BY_KIND,
    FEDERATION_ENTRYPOINTS_FILE,
    QUEST_DISPATCH_HINTS_FILE,
    REPO_ROOT,
    RETURN_NAVIGATION_HINTS_FILE,
    RouterError,
    build_federation_entrypoints_payload,
    build_quest_dispatch_hints_payload,
    build_kag_source_lift_relation_hints_payload,
    build_pairing_hints_payload,
    build_recommended_paths_payload,
    build_return_navigation_hints_payload,
    build_router_payload,
    build_tiny_model_entrypoints_payload,
    build_task_to_tier_hints_payload,
    build_task_to_surface_hints_payload,
    ensure_bool,
    ensure_int,
    ensure_list,
    ensure_mapping,
    ensure_repo_relative_path,
    ensure_string,
    ensure_string_list,
    load_technique_catalog_entries,
    load_json_file,
    relative_posix,
    require_keys,
    sort_registry_entries,
    write_json_file,
)


TECHNIQUE_SOURCE_TYPE = "generated-catalog"
SKILL_SOURCE_TYPE = "generated-catalog"
EVAL_SOURCE_TYPE = "generated-catalog"
MEMO_SOURCE_TYPE = "generated-catalog"
OWNER_LAYER_SHORTLIST_FILE = "generated/owner_layer_shortlist.min.json"
COMPOSITE_STRESS_ROUTE_HINTS_FILE = "generated/composite_stress_route_hints.min.json"
STATS_STRESS_RECOVERY_WINDOW_SUMMARY_FILE = "generated/stress_recovery_window_summary.min.json"
PLAYBOOK_STRESS_LANE_FILE = "examples/playbook_stress_lane.example.json"
PLAYBOOK_REENTRY_GATE_FILE = "examples/playbook_reentry_gate.example.json"
KAG_PROJECTION_HEALTH_FILE = "examples/projection_health_receipt.example.json"
KAG_REGROUNDING_TICKET_FILE = "examples/regrounding_ticket.example.json"
MEMO_OBJECT_CATALOG_FILE = "generated/memory_object_catalog.min.json"
MEMO_RECOVERY_PATTERN_MARKERS = (
    "stress-recovery-window",
    "recovery-pattern",
    "antifragility",
)
MEMO_REVIEW_READY_STATES = {"confirmed"}
MEMO_RECALL_READY_STATES = {"allowed", "preferred"}
OWNER_LAYER_SHORTLIST_SPECS: tuple[dict[str, str], ...] = (
    {
        "shortlist_id": "explicit-request.skills.primary",
        "signal": "explicit-request",
        "owner_repo": "aoa-skills",
        "object_kind": "skill",
        "target_surface": "aoa-skills.runtime_discovery_index",
        "inspect_surface": "aoa-skills.runtime_discovery_index",
        "hint_reason": "explicit owner-layer request for skills should stay on the bounded execution layer first",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.evals.primary",
        "signal": "explicit-request",
        "owner_repo": "aoa-evals",
        "object_kind": "eval",
        "target_surface": "aoa-evals.runtime_candidate_template_index.min",
        "inspect_surface": "aoa-evals.runtime_candidate_template_index.min",
        "hint_reason": "explicit owner-layer request for proof should inspect eval surfaces before inventing a new path",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.memo.primary",
        "signal": "explicit-request",
        "owner_repo": "aoa-memo",
        "object_kind": "memo",
        "target_surface": "aoa-memo.memory_catalog.min",
        "inspect_surface": "aoa-memo.memory_catalog.min",
        "hint_reason": "explicit owner-layer request for recall should inspect memo catalog surfaces directly",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.playbooks.primary",
        "signal": "explicit-request",
        "owner_repo": "aoa-playbooks",
        "object_kind": "playbook",
        "target_surface": "aoa-playbooks.playbook_registry.min",
        "inspect_surface": "aoa-playbooks.playbook_registry.min",
        "hint_reason": "explicit owner-layer request for recurring scenarios should inspect playbook registry surfaces directly",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.agents.primary",
        "signal": "explicit-request",
        "owner_repo": "aoa-agents",
        "object_kind": "agent",
        "target_surface": "aoa-agents.runtime_seam_bindings",
        "inspect_surface": "aoa-agents.runtime_seam_bindings",
        "hint_reason": "explicit owner-layer request for role posture should inspect agent runtime seam bindings",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.techniques.primary",
        "signal": "explicit-request",
        "owner_repo": "aoa-techniques",
        "object_kind": "technique",
        "target_surface": "aoa-techniques.technique_promotion_readiness.min",
        "inspect_surface": "aoa-techniques.technique_promotion_readiness.min",
        "hint_reason": "explicit owner-layer request for reuse should inspect technique promotion readiness rather than guess from routing",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.sdk.primary",
        "signal": "explicit-request",
        "owner_repo": "aoa-sdk",
        "object_kind": "runtime_surface",
        "target_surface": "aoa-sdk.workspace_control_plane.min",
        "inspect_surface": "aoa-sdk.workspace_control_plane.min",
        "hint_reason": "explicit control-plane requests should inspect aoa-sdk before widening into runtime or profile lanes",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.stats.primary",
        "signal": "explicit-request",
        "owner_repo": "aoa-stats",
        "object_kind": "runtime_surface",
        "target_surface": "aoa-stats.summary_surface_catalog.min",
        "inspect_surface": "aoa-stats.summary_surface_catalog.min",
        "hint_reason": "explicit derived-observability requests should inspect aoa-stats summary surfaces directly",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.seed.primary",
        "signal": "explicit-request",
        "owner_repo": "Dionysus",
        "object_kind": "seed",
        "target_surface": "Dionysus.seed_route_map.min",
        "inspect_surface": "Dionysus.seed_route_map.min",
        "hint_reason": "explicit seed or staging requests should inspect the Dionysus seed route map before crossing into owner repos",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.runtime.primary",
        "signal": "explicit-request",
        "owner_repo": "abyss-stack",
        "object_kind": "runtime_surface",
        "target_surface": "abyss-stack.diagnostic_surface_catalog.min",
        "inspect_surface": "abyss-stack.diagnostic_surface_catalog.min",
        "hint_reason": "explicit runtime-body requests should inspect the abyss-stack diagnostic surface catalog instead of inferring runtime authority from routing",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "explicit-request.profile.primary",
        "signal": "explicit-request",
        "owner_repo": "8Dionysus",
        "object_kind": "orientation_surface",
        "target_surface": "8Dionysus.public_route_map.min",
        "inspect_surface": "8Dionysus.public_route_map.min",
        "hint_reason": "explicit profile-orientation requests should inspect the public route map before treating the profile as an authority layer",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "proof-need.evals.primary",
        "signal": "proof-need",
        "owner_repo": "aoa-evals",
        "object_kind": "eval",
        "target_surface": "aoa-evals.runtime_candidate_template_index.min",
        "inspect_surface": "aoa-evals.runtime_candidate_template_index.min",
        "hint_reason": "proof-heavy intent usually wants an eval-owned inspect surface first",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "proof-need.skills.adjacent",
        "signal": "proof-need",
        "owner_repo": "aoa-skills",
        "object_kind": "skill",
        "target_surface": "aoa-skills.runtime_discovery_index",
        "inspect_surface": "aoa-skills.runtime_discovery_index",
        "hint_reason": "some proof-shaped routes are still bounded skill execution slices, so keep the skill lane visible as an adjacent option",
        "confidence": "low",
        "ambiguity": "ambiguous",
    },
    {
        "shortlist_id": "recall-need.memo.primary",
        "signal": "recall-need",
        "owner_repo": "aoa-memo",
        "object_kind": "memo",
        "target_surface": "aoa-memo.memory_catalog.min",
        "inspect_surface": "aoa-memo.memory_catalog.min",
        "hint_reason": "recall or provenance posture should inspect memo surfaces first",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "recall-need.memory-readiness-boundary.primary",
        "signal": "recall-need",
        "owner_repo": "aoa-memo",
        "object_kind": "memo",
        "target_surface": "aoa-memo.memo_registry.min",
        "inspect_surface": "aoa-memo.memo_registry.min",
        "hint_reason": (
            "future memory readiness pressure around durable consequences, deltas, retention, or live ledgers should inspect "
            "aoa-memo/docs/MEMORY_READINESS_BOUNDARY.md through the memo registry first; routing only "
            "points to the owner-held map, and memo readiness is not proof, KAG policy, or routing authority"
        ),
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "scenario-recurring.playbooks.primary",
        "signal": "scenario-recurring",
        "owner_repo": "aoa-playbooks",
        "object_kind": "playbook",
        "target_surface": "aoa-playbooks.playbook_registry.min",
        "inspect_surface": "aoa-playbooks.playbook_registry.min",
        "hint_reason": "recurring multi-step routes usually belong to playbook inspection before any promotion call",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "scenario-recurring.techniques.adjacent",
        "signal": "scenario-recurring",
        "owner_repo": "aoa-techniques",
        "object_kind": "technique",
        "target_surface": "aoa-techniques.technique_promotion_readiness.min",
        "inspect_surface": "aoa-techniques.technique_promotion_readiness.min",
        "hint_reason": "some recurring scenarios are really repeated bounded discipline, so keep technique promotion visible as an adjacent read",
        "confidence": "medium",
        "ambiguity": "ambiguous",
    },
    {
        "shortlist_id": "role-posture.agents.primary",
        "signal": "role-posture",
        "owner_repo": "aoa-agents",
        "object_kind": "agent",
        "target_surface": "aoa-agents.runtime_seam_bindings",
        "inspect_surface": "aoa-agents.runtime_seam_bindings",
        "hint_reason": "role and handoff posture work should inspect agent seam bindings first",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "repeated-pattern.techniques.primary",
        "signal": "repeated-pattern",
        "owner_repo": "aoa-techniques",
        "object_kind": "technique",
        "target_surface": "aoa-techniques.technique_promotion_readiness.min",
        "inspect_surface": "aoa-techniques.technique_promotion_readiness.min",
        "hint_reason": "repeated bounded discipline points toward technique promotion readiness first",
        "confidence": "high",
        "ambiguity": "clear",
    },
    {
        "shortlist_id": "repeated-pattern.playbooks.adjacent",
        "signal": "repeated-pattern",
        "owner_repo": "aoa-playbooks",
        "object_kind": "playbook",
        "target_surface": "aoa-playbooks.playbook_registry.min",
        "inspect_surface": "aoa-playbooks.playbook_registry.min",
        "hint_reason": "some repeated signals are really recurring scenarios, so keep playbooks visible as an adjacent shortlist target",
        "confidence": "medium",
        "ambiguity": "ambiguous",
    },
    {
        "shortlist_id": "risk-gate.skills.primary",
        "signal": "risk-gate",
        "owner_repo": "aoa-skills",
        "object_kind": "skill",
        "target_surface": "aoa-skills.runtime_discovery_index",
        "inspect_surface": "aoa-skills.runtime_discovery_index",
        "hint_reason": "risk-gate signals stay skill-first even when the route later hands off to owner layers",
        "confidence": "medium",
        "ambiguity": "clear",
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build aoa-routing generated surfaces.")
    parser.add_argument(
        "--techniques-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-techniques",
        help="Path to the aoa-techniques repository root.",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-skills",
        help="Path to the aoa-skills repository root.",
    )
    parser.add_argument(
        "--evals-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-evals",
        help="Path to the aoa-evals repository root.",
    )
    parser.add_argument(
        "--memo-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-memo",
        help="Path to the aoa-memo repository root for bounded memo routing surfaces.",
    )
    parser.add_argument(
        "--stats-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-stats",
        help="Path to the aoa-stats repository root for additive stress recovery summary surfaces.",
    )
    parser.add_argument(
        "--agents-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-agents",
        help="Path to the aoa-agents repository root for model-tier contracts.",
    )
    parser.add_argument(
        "--aoa-root",
        type=Path,
        default=REPO_ROOT.parent / "Agents-of-Abyss",
        help="Path to the Agents-of-Abyss repository root for federation root entry surfaces.",
    )
    parser.add_argument(
        "--playbooks-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-playbooks",
        help="Path to the aoa-playbooks repository root for federation playbook entries.",
    )
    parser.add_argument(
        "--kag-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-kag",
        help="Path to the aoa-kag repository root for federation KAG entry views.",
    )
    parser.add_argument(
        "--tos-root",
        type=Path,
        default=REPO_ROOT.parent / "Tree-of-Sophia",
        help="Path to the Tree-of-Sophia repository root for federation root entry surfaces.",
    )
    parser.add_argument(
        "--sdk-root",
        type=Path,
        default=REPO_ROOT.parent / "aoa-sdk",
        help="Path to the aoa-sdk repository root for runtime control-plane federation entries.",
    )
    parser.add_argument(
        "--seed-root",
        type=Path,
        default=REPO_ROOT.parent / "Dionysus",
        help="Path to the Dionysus repository root for seed federation entries.",
    )
    parser.add_argument(
        "--profile-root",
        type=Path,
        default=REPO_ROOT.parent / "8Dionysus",
        help="Path to the 8Dionysus repository root for public orientation federation entries.",
    )
    parser.add_argument(
        "--abyss-stack-root",
        type=Path,
        default=Path.home() / "src" / "abyss-stack",
        help="Path to the abyss-stack source checkout for runtime federation entries.",
    )
    parser.add_argument(
        "--generated-dir",
        type=Path,
        default=REPO_ROOT / "generated",
        help="Directory where generated outputs should be written.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that the generated directory already matches the canonical rebuild instead of rewriting files.",
    )
    return parser.parse_args()


def render_output_text(filename: str, payload: Any) -> str:
    if filename.endswith(".jsonl"):
        return dump_jsonl(payload)
    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=None,
        separators=(",", ":"),
        sort_keys=False,
    ) + "\n"


def validate_generated_dir_matches_outputs(
    outputs: dict[str, Any],
    *,
    generated_dir: Path,
) -> list[str]:
    mismatches: list[str] = []
    for filename, payload in outputs.items():
        path = generated_dir / filename
        if not path.exists():
            mismatches.append(f"missing generated output: {relative_posix(path)}")
            continue
        actual_text = path.read_text(encoding="utf-8")
        try:
            if filename.endswith(".jsonl"):
                actual_payload = [
                    json.loads(line)
                    for line in actual_text.splitlines()
                    if line.strip()
                ]
            else:
                actual_payload = json.loads(actual_text)
        except json.JSONDecodeError:
            mismatches.append(f"invalid generated output: {relative_posix(path)}")
            continue
        if actual_payload != payload:
            mismatches.append(f"stale generated output: {relative_posix(path)}")
    return mismatches


def collect_technique_entries(techniques_root: Path) -> list[dict[str, Any]]:
    catalog_path = techniques_root / "generated" / "technique_catalog.min.json"
    payload = ensure_mapping(load_json_file(catalog_path), relative_posix(catalog_path))
    techniques = ensure_list(payload.get("techniques"), f"{relative_posix(catalog_path)}.techniques")

    entries: list[dict[str, Any]] = []
    required_keys = (
        "id",
        "name",
        "domain",
        "status",
        "summary",
        "maturity_score",
        "rigor_level",
        "reversibility",
        "review_required",
        "validation_strength",
        "export_ready",
        "technique_path",
    )
    for index, item in enumerate(techniques):
        location = f"{relative_posix(catalog_path)}.techniques[{index}]"
        technique = ensure_mapping(item, location)
        require_keys(technique, required_keys, location)
        entries.append(
            {
                "kind": "technique",
                "id": ensure_string(technique["id"], f"{location}.id"),
                "name": ensure_string(technique["name"], f"{location}.name"),
                "repo": CANONICAL_REPO_BY_KIND["technique"],
                "path": ensure_repo_relative_path(
                    technique["technique_path"], f"{location}.technique_path"
                ),
                "status": ensure_string(technique["status"], f"{location}.status"),
                "summary": ensure_string(technique["summary"], f"{location}.summary"),
                "source_type": TECHNIQUE_SOURCE_TYPE,
                "attributes": {
                    "domain": ensure_string(technique["domain"], f"{location}.domain"),
                    "maturity_score": ensure_int(
                        technique["maturity_score"], f"{location}.maturity_score"
                    ),
                    "rigor_level": ensure_string(
                        technique["rigor_level"], f"{location}.rigor_level"
                    ),
                    "reversibility": ensure_string(
                        technique["reversibility"], f"{location}.reversibility"
                    ),
                    "review_required": ensure_bool(
                        technique["review_required"], f"{location}.review_required"
                    ),
                    "validation_strength": ensure_string(
                        technique["validation_strength"],
                        f"{location}.validation_strength",
                    ),
                    "export_ready": ensure_bool(
                        technique["export_ready"], f"{location}.export_ready"
                    ),
                },
            }
        )
    return entries


def collect_skill_entries(skills_root: Path) -> list[dict[str, Any]]:
    catalog_path = skills_root / "generated" / "skill_catalog.min.json"
    payload = ensure_mapping(load_json_file(catalog_path), relative_posix(catalog_path))
    skills = ensure_list(payload.get("skills"), f"{relative_posix(catalog_path)}.skills")
    entries: list[dict[str, Any]] = []
    required_keys = (
        "name",
        "scope",
        "status",
        "summary",
        "invocation_mode",
        "technique_dependencies",
        "skill_path",
    )
    for index, item in enumerate(skills):
        location = f"{relative_posix(catalog_path)}.skills[{index}]"
        skill = ensure_mapping(item, location)
        require_keys(skill, required_keys, location)
        skill_name = ensure_string(skill["name"], f"{location}.name")
        technique_dependencies = ensure_string_list(
            skill["technique_dependencies"],
            f"{location}.technique_dependencies",
        )
        entries.append(
            {
                "kind": "skill",
                "id": skill_name,
                "name": skill_name,
                "repo": CANONICAL_REPO_BY_KIND["skill"],
                "path": ensure_repo_relative_path(skill["skill_path"], f"{location}.skill_path"),
                "status": ensure_string(skill["status"], f"{location}.status"),
                "summary": ensure_string(skill["summary"], f"{location}.summary"),
                "source_type": SKILL_SOURCE_TYPE,
                "attributes": {
                    "scope": ensure_string(skill["scope"], f"{location}.scope"),
                    "invocation_mode": ensure_string(
                        skill["invocation_mode"],
                        f"{location}.invocation_mode",
                    ),
                    "technique_dependencies": technique_dependencies,
                },
            }
        )
    return entries


def collect_eval_entries(evals_root: Path) -> list[dict[str, Any]]:
    catalog_path = evals_root / "generated" / "eval_catalog.min.json"
    payload = ensure_mapping(load_json_file(catalog_path), relative_posix(catalog_path))
    evals = ensure_list(payload.get("evals"), f"{relative_posix(catalog_path)}.evals")
    entries: list[dict[str, Any]] = []
    required_keys = (
        "name",
        "category",
        "status",
        "summary",
        "object_under_evaluation",
        "claim_type",
        "baseline_mode",
        "verdict_shape",
        "report_format",
        "review_required",
        "validation_strength",
        "export_ready",
        "technique_dependencies",
        "skill_dependencies",
        "eval_path",
    )
    for index, item in enumerate(evals):
        location = f"{relative_posix(catalog_path)}.evals[{index}]"
        evaluation = ensure_mapping(item, location)
        require_keys(evaluation, required_keys, location)
        eval_name = ensure_string(evaluation["name"], f"{location}.name")
        technique_dependencies = ensure_string_list(
            evaluation["technique_dependencies"],
            f"{location}.technique_dependencies",
        )
        skill_dependencies = ensure_string_list(
            evaluation["skill_dependencies"],
            f"{location}.skill_dependencies",
        )
        entries.append(
            {
                "kind": "eval",
                "id": eval_name,
                "name": eval_name,
                "repo": CANONICAL_REPO_BY_KIND["eval"],
                "path": ensure_repo_relative_path(evaluation["eval_path"], f"{location}.eval_path"),
                "status": ensure_string(evaluation["status"], f"{location}.status"),
                "summary": ensure_string(evaluation["summary"], f"{location}.summary"),
                "source_type": EVAL_SOURCE_TYPE,
                "attributes": {
                    "category": ensure_string(
                        evaluation["category"], f"{location}.category"
                    ),
                    "object_under_evaluation": ensure_string(
                        evaluation["object_under_evaluation"],
                        f"{location}.object_under_evaluation",
                    ),
                    "claim_type": ensure_string(
                        evaluation["claim_type"], f"{location}.claim_type"
                    ),
                    "baseline_mode": ensure_string(
                        evaluation["baseline_mode"],
                        f"{location}.baseline_mode",
                    ),
                    "verdict_shape": ensure_string(
                        evaluation["verdict_shape"], f"{location}.verdict_shape"
                    ),
                    "review_required": ensure_bool(
                        evaluation["review_required"],
                        f"{location}.review_required",
                    ),
                    "validation_strength": ensure_string(
                        evaluation["validation_strength"],
                        f"{location}.validation_strength",
                    ),
                    "export_ready": ensure_bool(
                        evaluation["export_ready"], f"{location}.export_ready"
                    ),
                    "technique_dependencies": technique_dependencies,
                    "skill_dependencies": skill_dependencies,
                },
            }
        )
    return entries


def collect_memo_entries(memo_root: Path) -> list[dict[str, Any]]:
    catalog_path = memo_root / "generated" / "memory_catalog.min.json"
    payload = ensure_mapping(load_json_file(catalog_path), relative_posix(catalog_path))
    memo_surfaces = ensure_list(
        payload.get("memo_surfaces"),
        f"{relative_posix(catalog_path)}.memo_surfaces",
    )
    entries: list[dict[str, Any]] = []
    required_keys = (
        "id",
        "name",
        "surface_kind",
        "summary",
        "primary_focus",
        "recall_modes",
        "status",
        "temperature",
        "inspect_surface",
        "expand_surface",
        "source_path",
    )
    for index, item in enumerate(memo_surfaces):
        location = f"{relative_posix(catalog_path)}.memo_surfaces[{index}]"
        surface = ensure_mapping(item, location)
        require_keys(surface, required_keys, location)
        entries.append(
            {
                "kind": "memo",
                "id": ensure_string(surface["id"], f"{location}.id"),
                "name": ensure_string(surface["name"], f"{location}.name"),
                "repo": CANONICAL_REPO_BY_KIND["memo"],
                "path": ensure_repo_relative_path(surface["source_path"], f"{location}.source_path"),
                "status": ensure_string(surface["status"], f"{location}.status"),
                "summary": ensure_string(surface["summary"], f"{location}.summary"),
                "source_type": MEMO_SOURCE_TYPE,
                "attributes": {
                    "surface_kind": ensure_string(
                        surface["surface_kind"], f"{location}.surface_kind"
                    ),
                    "primary_focus": ensure_string(
                        surface["primary_focus"], f"{location}.primary_focus"
                    ),
                    "recall_modes": ensure_string_list(
                        surface["recall_modes"], f"{location}.recall_modes"
                    ),
                    "temperature": ensure_string(
                        surface["temperature"], f"{location}.temperature"
                    ),
                    "inspect_surface": ensure_repo_relative_path(
                        surface["inspect_surface"], f"{location}.inspect_surface"
                    ),
                    "expand_surface": ensure_repo_relative_path(
                        surface["expand_surface"], f"{location}.expand_surface"
                    ),
                },
            }
        )
    return entries


def load_required_mapping(path: Path) -> dict[str, Any]:
    return ensure_mapping(load_json_file(path), relative_posix(path))


def load_recovery_pattern_contexts(memo_root: Path) -> list[dict[str, Any]]:
    catalog_path = memo_root / MEMO_OBJECT_CATALOG_FILE
    payload = load_required_mapping(catalog_path)
    memory_objects = ensure_list(
        payload.get("memory_objects"),
        f"{relative_posix(catalog_path)}.memory_objects",
    )
    contexts: list[dict[str, Any]] = []
    for index, item in enumerate(memory_objects):
        location = f"{relative_posix(catalog_path)}.memory_objects[{index}]"
        memory_object = ensure_mapping(item, location)
        kind = ensure_string(memory_object.get("kind"), f"{location}.kind")
        if kind != "pattern":
            continue
        memory_id = ensure_string(memory_object.get("id"), f"{location}.id")
        source_path = ensure_repo_relative_path(
            memory_object.get("source_path"),
            f"{location}.source_path",
        )
        review_state = ensure_string(
            memory_object.get("review_state"),
            f"{location}.review_state",
        )
        recall_status = ensure_string(
            memory_object.get("current_recall_status"),
            f"{location}.current_recall_status",
        )
        marker_text = f"{memory_id} {source_path}".lower()
        if not any(marker in marker_text for marker in MEMO_RECOVERY_PATTERN_MARKERS):
            continue
        if review_state not in MEMO_REVIEW_READY_STATES:
            continue
        if recall_status not in MEMO_RECALL_READY_STATES:
            continue
        contexts.append(
            {
                "memory_id": memory_id,
                "title": ensure_string(memory_object.get("title"), f"{location}.title"),
                "source_path": source_path,
                "review_state": review_state,
                "current_recall_status": recall_status,
            }
        )
    return contexts


def split_repo_surface_ref(ref: str, *, location: str) -> tuple[str, str]:
    value = ensure_string(ref, location)
    if value.startswith("repo:"):
        trimmed = value[len("repo:") :]
        repo, separator, surface = trimmed.partition("/")
        if not separator or not repo or not surface:
            raise RouterError(f"{location} must use repo:<repo>/<path> form")
        return repo, surface
    repo, separator, surface = value.partition("/")
    if not separator or not repo or not surface:
        raise RouterError(f"{location} must name <repo>/<path>")
    return repo, surface


def build_composite_stress_route_hints_payload(
    *,
    stats_root: Path,
    playbooks_root: Path,
    kag_root: Path,
    memo_root: Path,
) -> dict[str, Any]:
    stats_path = stats_root / STATS_STRESS_RECOVERY_WINDOW_SUMMARY_FILE
    playbook_lane_path = playbooks_root / PLAYBOOK_STRESS_LANE_FILE
    playbook_gate_path = playbooks_root / PLAYBOOK_REENTRY_GATE_FILE
    projection_health_path = kag_root / KAG_PROJECTION_HEALTH_FILE
    regrounding_ticket_path = kag_root / KAG_REGROUNDING_TICKET_FILE

    stats_summary = load_required_mapping(stats_path)
    playbook_lane = load_required_mapping(playbook_lane_path)
    playbook_gate = load_required_mapping(playbook_gate_path)
    projection_health = load_required_mapping(projection_health_path)
    regrounding_ticket = load_required_mapping(regrounding_ticket_path)
    memo_contexts = load_recovery_pattern_contexts(memo_root)

    stats_location = relative_posix(stats_path)
    scope = ensure_mapping(stats_summary.get("scope"), f"{stats_location}.scope")
    summary = ensure_mapping(stats_summary.get("summary"), f"{stats_location}.summary")
    inputs = ensure_mapping(stats_summary.get("inputs"), f"{stats_location}.inputs")
    suppression = ensure_mapping(
        stats_summary.get("suppression"),
        f"{stats_location}.suppression",
    )
    receipt_refs = ensure_string_list(
        inputs.get("receipt_refs", []),
        f"{stats_location}.inputs.receipt_refs",
    )
    eval_report_refs = ensure_string_list(
        inputs.get("eval_report_refs", []),
        f"{stats_location}.inputs.eval_report_refs",
    )
    trend_flags = ensure_string_list(
        stats_summary.get("trend_flags", []),
        f"{stats_location}.trend_flags",
    )

    if receipt_refs:
        owner_repo, owner_surface = split_repo_surface_ref(
            receipt_refs[0],
            location=f"{stats_location}.inputs.receipt_refs[0]",
        )
    else:
        gate_scope = ensure_mapping(playbook_gate.get("scope"), "playbook_reentry_gate.scope")
        owner_repo = ensure_string(gate_scope.get("repo"), "playbook_reentry_gate.scope.repo")
        owner_surface = ensure_string(
            gate_scope.get("surface"),
            "playbook_reentry_gate.scope.surface",
        )

    memo_pattern_refs = [context["source_path"] for context in memo_contexts]
    adjacent_source_refs = ensure_string_list(
        playbook_gate.get("required_evidence", []),
        "playbook_reentry_gate.required_evidence",
    ) + ensure_string_list(
        projection_health.get("source_fallback_refs", []),
        "projection_health_receipt.source_fallback_refs",
    )

    next_hops = [
        {
            "kind": "source_receipt",
            "target_repo": owner_repo,
            "target_surface": owner_surface,
            "reason": "Start from the source-owned stress receipt before trusting any downstream route overlay.",
            "bounded": True,
        },
        {
            "kind": "playbook_lane",
            "target_repo": "aoa-playbooks",
            "target_surface": PLAYBOOK_STRESS_LANE_FILE,
            "reason": "Use the structured degraded lane contract instead of reparsing authored playbook markdown.",
            "bounded": True,
        },
        {
            "kind": "reentry_gate",
            "target_repo": "aoa-playbooks",
            "target_surface": PLAYBOOK_REENTRY_GATE_FILE,
            "reason": "Re-entry posture stays source-owned by the explicit gate surface.",
            "bounded": True,
        },
        {
            "kind": "projection_health",
            "target_repo": "aoa-kag",
            "target_surface": KAG_PROJECTION_HEALTH_FILE,
            "reason": "Quarantined or degraded KAG posture must be read from the source-owned health receipt.",
            "bounded": True,
        },
        {
            "kind": "regrounding_ticket",
            "target_repo": "aoa-kag",
            "target_surface": KAG_REGROUNDING_TICKET_FILE,
            "reason": "Regrounding remains a bounded KAG repair plan, not a router-owned recovery action.",
            "bounded": True,
        },
    ]
    if memo_contexts:
        next_hops.append(
            {
                "kind": "memo_pattern",
                "target_repo": "aoa-memo",
                "target_surface": memo_contexts[0]["source_path"],
                "reason": "Reviewed recovery-pattern context may be recalled after source receipts and re-entry gates are named.",
                "bounded": True,
            }
        )

    hint = {
        "schema_version": "composite_stress_route_hint_v1",
        "hint_id": "composite-stress-route:"
        + ensure_string(scope.get("stressor_family"), f"{stats_location}.scope.stressor_family"),
        "stressor_family": ensure_string(
            scope.get("stressor_family"),
            f"{stats_location}.scope.stressor_family",
        ),
        "owner_surface": {
            "repo": owner_repo,
            "surface": owner_surface,
            "surface_family": ensure_string(
                scope.get("surface_family"),
                f"{stats_location}.scope.surface_family",
            ),
        },
        "preferred_posture": ensure_string(
            regrounding_ticket.get("return_posture"),
            "regrounding_ticket.return_posture",
        ),
        "input_refs": {
            "stats_summary_ref": f"aoa-stats:{STATS_STRESS_RECOVERY_WINDOW_SUMMARY_FILE}",
            "playbook_lane_ref": f"aoa-playbooks:{PLAYBOOK_STRESS_LANE_FILE}",
            "reentry_gate_ref": f"aoa-playbooks:{PLAYBOOK_REENTRY_GATE_FILE}",
            "projection_health_ref": f"aoa-kag:{KAG_PROJECTION_HEALTH_FILE}",
            "regrounding_ticket_ref": f"aoa-kag:{KAG_REGROUNDING_TICKET_FILE}",
            "memo_pattern_refs": [f"aoa-memo:{path}" for path in memo_pattern_refs],
        },
        "route_status": {
            "stats_suppression_status": ensure_string(
                suppression.get("status"),
                f"{stats_location}.suppression.status",
            ),
            "projection_health_state": ensure_string(
                projection_health.get("health_state"),
                "projection_health_receipt.health_state",
            ),
            "consumer_posture": ensure_string(
                projection_health.get("consumer_posture"),
                "projection_health_receipt.consumer_posture",
            ),
            "reentry_decision": ensure_string(
                playbook_gate.get("decision"),
                "playbook_reentry_gate.decision",
            ),
            "regrounding_status": ensure_string(
                regrounding_ticket.get("status"),
                "regrounding_ticket.status",
            ),
            "route_discipline": summary.get("route_discipline"),
            "reentry_quality": summary.get("reentry_quality"),
            "regrounding_effectiveness": summary.get("regrounding_effectiveness"),
            "trend_flags": trend_flags,
        },
        "source_priority": {
            "owner_receipt_refs": receipt_refs,
            "proof_refs": eval_report_refs,
            "adjacent_source_refs": adjacent_source_refs,
            "routing_is_advisory": True,
        },
        "next_hops": next_hops,
        "memo_context": memo_contexts,
        "notes": "Additive stress-route overlay only; do not let this surface override thin-router defaults or source-owned evidence.",
    }

    return {
        "schema_version": "aoa_routing_composite_stress_route_hints_v1",
        "source_inputs": [
            {
                "repo": "aoa-stats",
                "surface_kind": "stress_recovery_window_summary",
                "ref": STATS_STRESS_RECOVERY_WINDOW_SUMMARY_FILE,
            },
            {
                "repo": "aoa-playbooks",
                "surface_kind": "playbook_stress_lane",
                "ref": PLAYBOOK_STRESS_LANE_FILE,
            },
            {
                "repo": "aoa-playbooks",
                "surface_kind": "playbook_reentry_gate",
                "ref": PLAYBOOK_REENTRY_GATE_FILE,
            },
            {
                "repo": "aoa-kag",
                "surface_kind": "projection_health_receipt",
                "ref": KAG_PROJECTION_HEALTH_FILE,
            },
            {
                "repo": "aoa-kag",
                "surface_kind": "regrounding_ticket",
                "ref": KAG_REGROUNDING_TICKET_FILE,
            },
            {
                "repo": "aoa-memo",
                "surface_kind": "memory_object_catalog",
                "ref": MEMO_OBJECT_CATALOG_FILE,
            },
        ],
        "hints": [hint],
    }


def dump_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


def build_owner_layer_shortlist_payload() -> dict[str, Any]:
    return {
        "schema_version": "aoa_routing_owner_layer_shortlist_v2",
        "schema_ref": "schemas/owner-layer-shortlist.schema.json",
        "owner_repo": "aoa-routing",
        "surface_kind": "owner_layer_shortlist",
        "hints": [dict(spec) for spec in OWNER_LAYER_SHORTLIST_SPECS],
    }


def build_outputs(
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
    stats_root: Path,
    agents_root: Path,
    aoa_root: Path,
    playbooks_root: Path,
    kag_root: Path,
    tos_root: Path,
    sdk_root: Path | None = None,
    seed_root: Path | None = None,
    profile_root: Path | None = None,
    abyss_stack_root: Path | None = None,
    routing_root: Path | None = None,
) -> dict[str, dict[str, Any] | list[dict[str, Any]]]:
    routing_root = (routing_root or REPO_ROOT).resolve()
    sdk_root = sdk_root or (routing_root.parent / "aoa-sdk")
    seed_root = seed_root or (routing_root.parent / "Dionysus")
    profile_root = profile_root or (routing_root.parent / "8Dionysus")
    abyss_stack_root = abyss_stack_root or (Path.home() / "src" / "abyss-stack")
    technique_catalog_source, technique_catalog_entries = load_technique_catalog_entries(
        techniques_root
    )
    registry_entries = sort_registry_entries(
        collect_technique_entries(techniques_root)
        + collect_skill_entries(skills_root)
        + collect_eval_entries(evals_root)
        + collect_memo_entries(memo_root)
    )
    seen: set[tuple[str, str]] = set()
    for entry in registry_entries:
        key = (entry["kind"], entry["id"])
        if key in seen:
            raise RouterError(f"duplicate registry entry for {entry['kind']}:{entry['id']}")
        seen.add(key)

    registry_payload = {
        "registry_version": 1,
        "reserved_kinds": [],
        "entries": registry_entries,
    }
    router_payload = build_router_payload(registry_entries)
    hints_payload = build_task_to_surface_hints_payload(memo_root)
    tier_hints_payload = build_task_to_tier_hints_payload(agents_root)
    quest_dispatch_hints_payload = build_quest_dispatch_hints_payload(
        techniques_root,
        skills_root,
        evals_root,
    )
    federation_entrypoints_payload = build_federation_entrypoints_payload(
        aoa_root,
        techniques_root,
        agents_root,
        playbooks_root,
        kag_root,
        tos_root,
        sdk_root,
        stats_root,
        seed_root,
        profile_root,
        abyss_stack_root,
    )
    return_navigation_payload = build_return_navigation_hints_payload(
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        aoa_root,
        stats_root,
        agents_root,
        playbooks_root,
        kag_root,
        tos_root,
        sdk_root,
        seed_root,
        profile_root,
        abyss_stack_root,
        hints_payload,
        federation_entrypoints_payload,
    )
    recommended_payload = build_recommended_paths_payload(registry_entries)
    relation_hints_payload = build_kag_source_lift_relation_hints_payload(
        registry_entries,
        technique_catalog_source,
        technique_catalog_entries,
    )
    composite_stress_route_hints_payload = build_composite_stress_route_hints_payload(
        stats_root=stats_root,
        playbooks_root=playbooks_root,
        kag_root=kag_root,
        memo_root=memo_root,
    )
    owner_layer_shortlist_payload = build_owner_layer_shortlist_payload()
    pairing_payload = build_pairing_hints_payload(
        registry_entries,
        technique_catalog_source,
        technique_catalog_entries,
    )
    tiny_model_entrypoints_payload = build_tiny_model_entrypoints_payload(
        registry_entries,
        hints_payload,
        federation_entrypoints_payload,
    )
    outputs = {
        "cross_repo_registry.min.json": registry_payload,
        "aoa_router.min.json": router_payload,
        "task_to_surface_hints.json": hints_payload,
        "task_to_tier_hints.json": tier_hints_payload,
        Path(QUEST_DISPATCH_HINTS_FILE).name: quest_dispatch_hints_payload,
        Path(FEDERATION_ENTRYPOINTS_FILE).name: federation_entrypoints_payload,
        Path(RETURN_NAVIGATION_HINTS_FILE).name: return_navigation_payload,
        "recommended_paths.min.json": recommended_payload,
        "kag_source_lift_relation_hints.min.json": relation_hints_payload,
        Path(COMPOSITE_STRESS_ROUTE_HINTS_FILE).name: composite_stress_route_hints_payload,
        Path(OWNER_LAYER_SHORTLIST_FILE).name: owner_layer_shortlist_payload,
        "pairing_hints.min.json": pairing_payload,
        "tiny_model_entrypoints.json": tiny_model_entrypoints_payload,
    }
    outputs.update(
        build_two_stage_outputs(
            routing_root=routing_root,
            skills_root=skills_root,
            tiny_model_entrypoints=tiny_model_entrypoints_payload,
            aoa_router=router_payload,
            pairing_hints=pairing_payload,
            task_to_surface_hints=hints_payload,
        )
    )
    return outputs


def main() -> int:
    args = parse_args()
    outputs = build_outputs(
        args.techniques_root.resolve(),
        args.skills_root.resolve(),
        args.evals_root.resolve(),
        args.memo_root.resolve(),
        args.stats_root.resolve(),
        args.agents_root.resolve(),
        args.aoa_root.resolve(),
        args.playbooks_root.resolve(),
        args.kag_root.resolve(),
        args.tos_root.resolve(),
        args.sdk_root.resolve(),
        args.seed_root.resolve(),
        args.profile_root.resolve(),
        args.abyss_stack_root.resolve(),
        REPO_ROOT.resolve(),
    )
    generated_dir = args.generated_dir.resolve()
    generated_dir.mkdir(parents=True, exist_ok=True)

    if args.check:
        mismatches = validate_generated_dir_matches_outputs(outputs, generated_dir=generated_dir)
        if mismatches:
            raise RouterError("; ".join(mismatches))
        for filename in outputs:
            print(f"[ok] verified {relative_posix(generated_dir / filename)}")
        return 0

    for filename, payload in outputs.items():
        path = generated_dir / filename
        rendered_text = render_output_text(filename, payload)
        if path.exists():
            try:
                actual_text = path.read_text(encoding="utf-8")
                if filename.endswith(".jsonl"):
                    actual_payload = [
                        json.loads(line)
                        for line in actual_text.splitlines()
                        if line.strip()
                    ]
                else:
                    actual_payload = json.loads(actual_text)
                if actual_payload == payload:
                    continue
            except json.JSONDecodeError:
                pass
        path.write_text(rendered_text, encoding="utf-8", newline="\n")
        print(f"[ok] wrote {relative_posix(path)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RouterError as exc:
        print(f"[error] {exc}")
        raise SystemExit(1)
