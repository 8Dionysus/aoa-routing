#!/usr/bin/env python3
"""Validate aoa-routing generated surfaces."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

import validate_nested_agents
from validate_two_stage_skill_router import validate_outputs as validate_two_stage_outputs

from build_router import build_outputs
from router_core import (
    ACTIVE_KINDS,
    AOA_TECHNIQUES_KAG_VIEW_EXAMPLE_OBJECT_IDS,
    AGENT_REGISTRY_PATH,
    AGENTS_REPO,
    ALL_KINDS,
    AOA_ROOT_REPO,
    CANONICAL_REPO_BY_KIND,
    DIRECT_RELATION_TYPES_SET,
    FEDERATION_ACTIVE_ENTRY_KINDS,
    FEDERATION_DECLARED_ENTRY_KINDS,
    FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID,
    FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID,
    FEDERATION_DEFAULT_TIER_ENTRY_ID,
    FEDERATION_ENTRYPOINTS_FILE,
    FEDERATION_ROOT_IDS,
    KAG_REPO,
    KAG_SOURCE_LIFT_TECHNIQUE_SET,
    MEMO_CAPSULE_RECALL_MODES,
    MEMO_INSPECT_SURFACE_FILE,
    MEMO_OBJECT_RECALL_DEFAULT_MODE,
    MEMO_OBJECT_RETURN_READY_CONTRACT,
    MEMO_OBJECT_EXPAND_SURFACE_FILE,
    MEMO_OBJECT_INSPECT_SURFACE_FILE,
    MEMO_OBJECT_RECALL_CONTRACTS_BY_MODE,
    MODEL_TIER_SOURCE_REPO,
    MODEL_TIER_REGISTRY_PATH,
    PAIRABLE_KINDS,
    PAIRING_SURFACE_REPO,
    PLAYBOOKS_REPO,
    QUEST_DISPATCH_HINTS_FILE,
    QUEST_ROUTING_ACTIONS_ENABLED,
    QUEST_ROUTING_CLOSED_STATES,
    QUEST_ROUTING_EXPAND_DOC_BY_REPO,
    QUEST_ROUTING_SOURCE_REPOS,
    QUEST_ROUTING_WAVE_SCOPE,
    RECOMMENDED_HOP_KINDS,
    REPO_ROOT,
    RESERVED_KINDS,
    RETURN_NAVIGATION_HINTS_FILE,
    RouterError,
    TOS_REPO,
    TOS_KAG_VIEW_ENTRY_ID,
    TOS_KAG_VIEW_PLAYBOOK_ENTRY_ID,
    TOS_ROUTE_RETRIEVAL_ID,
    TOS_ROUTE_RETRIEVAL_SURFACE_REF,
    TOS_TINY_ENTRY_DOCTRINE_PATH,
    TOS_TINY_ENTRY_ROUTE_ID,
    TOS_TINY_ENTRY_ROUTE_PATH,
    build_federation_entrypoints_payload,
    build_quest_dispatch_hints_payload,
    build_quest_routing_source_inputs,
    build_kag_source_lift_relation_hints_payload,
    build_pairing_hints_payload,
    build_recommended_paths_payload,
    build_return_navigation_hints_payload,
    build_router_payload,
    build_tiny_model_entrypoints_payload,
    build_task_to_tier_hints_payload,
    build_task_to_surface_hints_payload,
    collect_memo_recall_mode_order,
    ensure_bool,
    ensure_cross_repo_surface_ref,
    ensure_list,
    ensure_mapping,
    ensure_repo_relative_path,
    ensure_repo_qualified_ref,
    ensure_string,
    ensure_string_list,
    is_pending_technique_id,
    load_json_file,
    load_agent_registry_entries,
    load_live_quest_projection_entries,
    load_memo_catalog_surfaces,
    load_model_tier_entries,
    load_model_tier_registry,
    load_playbook_registry_entries,
    load_technique_catalog_entries,
    load_tos_tiny_entry_route,
)


@dataclass(frozen=True)
class ValidationIssue:
    location: str
    message: str


OUTPUT_SCHEMA_NAMES = {
    "cross_repo_registry.min.json": "cross-repo-registry.schema.json",
    "aoa_router.min.json": "aoa-router.schema.json",
    "task_to_surface_hints.json": "task-to-surface-hints.schema.json",
    "task_to_tier_hints.json": "task-to-tier-hints.schema.json",
    Path(QUEST_DISPATCH_HINTS_FILE).name: "quest-dispatch-hints.schema.json",
    Path(FEDERATION_ENTRYPOINTS_FILE).name: "federation-entrypoints.schema.json",
    Path(RETURN_NAVIGATION_HINTS_FILE).name: "return-navigation-hints.schema.json",
    "recommended_paths.min.json": "recommended-paths.schema.json",
    "kag_source_lift_relation_hints.min.json": "kag-source-lift-relation-hints.schema.json",
    "pairing_hints.min.json": "pairing-hints.schema.json",
    "tiny_model_entrypoints.json": "tiny-model-entrypoints.schema.json",
    "two_stage_skill_entrypoints.json": "two-stage-skill-entrypoints.schema.json",
    "two_stage_router_prompt_blocks.json": "two-stage-router-prompt-blocks.schema.json",
    "two_stage_router_tool_schemas.json": "two-stage-router-tool-schemas.schema.json",
    "two_stage_router_examples.json": "two-stage-router-examples.schema.json",
    "two_stage_router_manifest.json": "two-stage-router-manifest.schema.json",
}

SOURCE_OWNED_PAYLOAD_KEYS = (
    "content_markdown",
    "sections",
    "technique_path",
    "skill_path",
    "eval_path",
    "one_line_intent",
    "use_when_short",
    "do_not_use_short",
    "inputs_short",
    "outputs_short",
    "core_contract_short",
    "main_risk_short",
    "validation_short",
    "trigger_boundary_short",
    "workflow_short",
    "main_anti_patterns_short",
    "verification_short",
    "bounded_claim_short",
    "blind_spot_short",
    "what_this_does_not_prove",
)

EXPECTED_KAG_VIEW_IDS = {
    FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID,
    TOS_KAG_VIEW_ENTRY_ID,
}
FOUNDATION_ROUTING_QUEST_IDS = ("AOA-RT-Q-0001", "AOA-RT-Q-0002")
REQUIRED_ROUTING_QUEST_IDS = FOUNDATION_ROUTING_QUEST_IDS
REQUIRED_ROUTING_SEAM_SNIPPETS = (
    "Source repos own quest meaning.",
    "`aoa-routing` may only consume thin, derived quest projections from live generated quest surfaces.",
    "- parse live `quests/*.yaml` as authority",
    "- `generated/quest_catalog.min.json`",
    "- `generated/quest_dispatch.min.json`",
    "The first live quest-routing wave is source-only.",
    "Production routing does not read `.example.json` quest fixtures.",
    "The only live quest actions in this wave are `inspect`, `expand`, and `handoff`.",
    "`pair` and `recall` belong to later routing waves.",
)
REQUIRED_QUEST_SCHEMA_TOP_LEVEL_KEYS = (
    "$schema",
    "$id",
    "title",
    "type",
    "additionalProperties",
    "required",
    "properties",
)
EXPECTED_QUEST_HINT_ACTION_ORDER = ["inspect", "expand", "handoff"]
EXPECTED_ROUTING_QUEST_STATES = {
    "AOA-RT-Q-0001": "done",
    "AOA-RT-Q-0002": "reanchor",
    "AOA-RT-Q-0003": "captured",
    "AOA-RT-Q-0004": "triaged",
}
REQUIRED_REANCHOR_NOTE_SNIPPET = (
    "no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist"
)
QUEST_BOARD_SCHEMA_NAME = "quest_board_entry.schema.json"
QUEST_BOARD_EXAMPLE_NAME = "quest_board.min.example.json"
QUEST_BOARD_REQUIRED_INPUT_REPOS = ("aoa-skills", "aoa-agents", "aoa-evals")
RPG_NAVIGATION_SCHEMA_NAME = "rpg_navigation_bundle.schema.json"
RPG_NAVIGATION_EXAMPLE_NAME = "rpg_navigation.min.example.json"
RPG_NAVIGATION_DOC_NAME = "docs/RPG_NAVIGATION_BRIDGE.md"
RPG_NAVIGATION_REQUIRED_DOC_TOKENS = (
    "## Core rule",
    "Routing owns navigation.",
    "Do not add reward verbs, completion verbs, or state-writing verbs here.",
    "Until live builders exist, keep this seam example-only and validator-shaped.",
)
RPG_NAVIGATION_REQUIRED_INPUTS = (
    ("aoa-playbooks", "quest_dispatch"),
    ("aoa-playbooks", "party_template_cards"),
    ("aoa-evals", "unlock_proof_cards"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate aoa-routing generated outputs.")
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
        help="Path to the aoa-memo repository root. Reserved only in v0.1.",
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
        help="Path to the Agents-of-Abyss repository root for federation root entry validation.",
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
        help="Path to the Tree-of-Sophia repository root for federation root entry validation.",
    )
    parser.add_argument(
        "--generated-dir",
        type=Path,
        default=REPO_ROOT / "generated",
        help="Directory containing generated outputs.",
    )
    return parser.parse_args()


@lru_cache(maxsize=None)
def load_schema(schema_name: str) -> dict[str, Any]:
    schema_path = REPO_ROOT / "schemas" / schema_name
    with schema_path.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=None)
def get_schema_registry() -> Registry:
    resources: list[tuple[str, Resource]] = []
    for schema_path in sorted((REPO_ROOT / "schemas").glob("*.schema.json")):
        schema = load_schema(schema_path.name)
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id.strip():
            raise RouterError(f"{schema_path.name} is missing a usable $id")
        resources.append((schema_id, Resource.from_contents(schema)))
    return Registry().with_resources(resources)


@lru_cache(maxsize=None)
def get_schema_validator(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(schema_name), registry=get_schema_registry())


def format_schema_path(path_parts: Iterable[Any]) -> str:
    parts: list[str] = []
    for part in path_parts:
        if isinstance(part, int):
            parts.append(f"[{part}]")
        else:
            if parts:
                parts.append(f".{part}")
            else:
                parts.append(str(part))
    return "".join(parts)


def validate_against_schema(
    data: Any,
    schema_name: str,
    location: str,
    issues: list[ValidationIssue],
) -> bool:
    validator = get_schema_validator(schema_name)
    schema_errors = sorted(
        validator.iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    for error in schema_errors:
        error_path = format_schema_path(error.absolute_path)
        if error_path:
            message = f"schema violation at '{error_path}': {error.message}"
        else:
            message = f"schema violation: {error.message}"
        issues.append(ValidationIssue(location, message))
    return not schema_errors


def load_output(path: Path, issues: list[ValidationIssue]) -> dict[str, Any] | None:
    try:
        payload = load_json_file(path)
    except RouterError as exc:
        issues.append(ValidationIssue(path.name, str(exc)))
        return None
    try:
        return ensure_mapping(payload, path.name)
    except RouterError as exc:
        issues.append(ValidationIssue(path.name, str(exc)))
        return None


def repo_relative(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def load_yaml_mapping(path: Path, issues: list[ValidationIssue], *, repo_root: Path) -> dict[str, Any] | None:
    if yaml is None:
        issues.append(ValidationIssue(repo_relative(repo_root, path), "PyYAML is required to validate questbook surfaces"))
        return None
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(ValidationIssue(repo_relative(repo_root, path), "missing required file"))
        return None
    except yaml.YAMLError as exc:
        issues.append(ValidationIssue(repo_relative(repo_root, path), f"invalid YAML: {exc}"))
        return None
    if not isinstance(payload, dict):
        issues.append(ValidationIssue(repo_relative(repo_root, path), "YAML payload must be an object"))
        return None
    return payload


def quest_sort_key(quest_id: str) -> tuple[int, str]:
    suffix = quest_id.rsplit("-", 1)[-1]
    try:
        return (int(suffix), quest_id)
    except ValueError:
        return (10**9, quest_id)


def discover_routing_quest_ids(repo_root: Path) -> list[str]:
    quest_ids = sorted(
        {
            path.stem
            for path in (repo_root / "quests").glob("AOA-RT-Q-*.yaml")
            if path.is_file()
        },
        key=quest_sort_key,
    )
    if not quest_ids:
        return list(FOUNDATION_ROUTING_QUEST_IDS)
    return quest_ids


def validate_adjunct_quest_board_surface(repo_root: Path, issues: list[ValidationIssue]) -> None:
    schema_path = repo_root / "schemas" / QUEST_BOARD_SCHEMA_NAME
    example_path = repo_root / "generated" / QUEST_BOARD_EXAMPLE_NAME

    try:
        schema_payload = load_json_file(schema_path)
        schema_object = ensure_mapping(schema_payload, repo_relative(repo_root, schema_path))
    except RouterError as exc:
        issues.append(ValidationIssue(repo_relative(repo_root, schema_path), str(exc)))
        return

    if schema_object.get("title") != "quest_board_entry_v1":
        issues.append(
            ValidationIssue(
                repo_relative(repo_root, schema_path),
                "schema title must stay 'quest_board_entry_v1'",
            )
        )
    try:
        Draft202012Validator.check_schema(schema_object)
    except SchemaError as exc:
        issues.append(ValidationIssue(repo_relative(repo_root, schema_path), f"invalid JSON schema: {exc.message}"))

    example_payload = load_output(example_path, issues)
    if example_payload is None:
        return

    if example_payload.get("version") != 1:
        issues.append(ValidationIssue(QUEST_BOARD_EXAMPLE_NAME, "version must stay 1"))
    if example_payload.get("authority") != "derived-example-only":
        issues.append(
            ValidationIssue(
                QUEST_BOARD_EXAMPLE_NAME,
                "authority must stay 'derived-example-only'",
            )
        )
    if example_payload.get("wave_scope") != "adjunct-rpg-first-wave":
        issues.append(
            ValidationIssue(
                QUEST_BOARD_EXAMPLE_NAME,
                "wave_scope must stay 'adjunct-rpg-first-wave'",
            )
        )

    try:
        inputs = ensure_list(example_payload.get("inputs"), f"{QUEST_BOARD_EXAMPLE_NAME}.inputs")
        entries = ensure_list(example_payload.get("entries"), f"{QUEST_BOARD_EXAMPLE_NAME}.entries")
    except RouterError as exc:
        issues.append(ValidationIssue(QUEST_BOARD_EXAMPLE_NAME, str(exc)))
        return

    input_repos: list[str] = []
    for index, raw_input in enumerate(inputs):
        location = f"{QUEST_BOARD_EXAMPLE_NAME}.inputs[{index}]"
        try:
            input_payload = ensure_mapping(raw_input, location)
        except RouterError as exc:
            issues.append(ValidationIssue(QUEST_BOARD_EXAMPLE_NAME, str(exc)))
            continue
        repo_name = input_payload.get("repo")
        if isinstance(repo_name, str):
            input_repos.append(repo_name)

    if tuple(input_repos) != QUEST_BOARD_REQUIRED_INPUT_REPOS:
        issues.append(
            ValidationIssue(
                QUEST_BOARD_EXAMPLE_NAME,
                "inputs must stay ordered as aoa-skills, aoa-agents, aoa-evals for the first adjunct example wave",
            )
        )

    for index, raw_entry in enumerate(entries):
        location = f"{QUEST_BOARD_EXAMPLE_NAME}.entries[{index}]"
        try:
            entry = ensure_mapping(raw_entry, location)
        except RouterError as exc:
            issues.append(ValidationIssue(QUEST_BOARD_EXAMPLE_NAME, str(exc)))
            continue
        validate_against_schema(entry, QUEST_BOARD_SCHEMA_NAME, location, issues)
        actions = entry.get("entry_actions")
        if actions != EXPECTED_QUEST_HINT_ACTION_ORDER:
            issues.append(
                ValidationIssue(
                    QUEST_BOARD_EXAMPLE_NAME,
                    f"{location}.entry_actions must stay exactly {EXPECTED_QUEST_HINT_ACTION_ORDER}",
                )
            )


def validate_rpg_navigation_bridge_surface(repo_root: Path, issues: list[ValidationIssue]) -> None:
    doc_path = repo_root / RPG_NAVIGATION_DOC_NAME
    schema_path = repo_root / "schemas" / RPG_NAVIGATION_SCHEMA_NAME
    example_path = repo_root / "generated" / RPG_NAVIGATION_EXAMPLE_NAME

    try:
        doc_text = doc_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(ValidationIssue(repo_relative(repo_root, doc_path), "missing required file"))
        return
    for token in RPG_NAVIGATION_REQUIRED_DOC_TOKENS:
        if token not in doc_text:
            issues.append(
                ValidationIssue(
                    repo_relative(repo_root, doc_path),
                    f"RPG navigation bridge note must mention '{token}'",
                )
            )

    try:
        schema_payload = load_json_file(schema_path)
        schema_object = ensure_mapping(schema_payload, repo_relative(repo_root, schema_path))
    except RouterError as exc:
        issues.append(ValidationIssue(repo_relative(repo_root, schema_path), str(exc)))
        return

    if schema_object.get("title") != "rpg_navigation_bundle_v1":
        issues.append(
            ValidationIssue(
                repo_relative(repo_root, schema_path),
                "schema title must stay 'rpg_navigation_bundle_v1'",
            )
        )
    try:
        Draft202012Validator.check_schema(schema_object)
    except SchemaError as exc:
        issues.append(ValidationIssue(repo_relative(repo_root, schema_path), f"invalid JSON schema: {exc.message}"))

    example_payload = load_output(example_path, issues)
    if example_payload is None:
        return
    validate_against_schema(example_payload, RPG_NAVIGATION_SCHEMA_NAME, RPG_NAVIGATION_EXAMPLE_NAME, issues)

    if example_payload.get("schema_version") != "rpg_navigation_bundle_v1":
        issues.append(ValidationIssue(RPG_NAVIGATION_EXAMPLE_NAME, "schema_version must stay 'rpg_navigation_bundle_v1'"))
    if example_payload.get("authority") != "derived-example-only":
        issues.append(ValidationIssue(RPG_NAVIGATION_EXAMPLE_NAME, "authority must stay 'derived-example-only'"))
    if example_payload.get("wave_scope") != "adjunct-rpg-bridge-wave":
        issues.append(ValidationIssue(RPG_NAVIGATION_EXAMPLE_NAME, "wave_scope must stay 'adjunct-rpg-bridge-wave'"))

    try:
        inputs = ensure_list(example_payload.get("inputs"), f"{RPG_NAVIGATION_EXAMPLE_NAME}.inputs")
        entries = ensure_list(example_payload.get("entries"), f"{RPG_NAVIGATION_EXAMPLE_NAME}.entries")
    except RouterError as exc:
        issues.append(ValidationIssue(RPG_NAVIGATION_EXAMPLE_NAME, str(exc)))
        return

    actual_inputs: list[tuple[str, str]] = []
    for index, raw_input in enumerate(inputs):
        location = f"{RPG_NAVIGATION_EXAMPLE_NAME}.inputs[{index}]"
        try:
            input_payload = ensure_mapping(raw_input, location)
        except RouterError as exc:
            issues.append(ValidationIssue(RPG_NAVIGATION_EXAMPLE_NAME, str(exc)))
            continue
        repo_name = input_payload.get("repo")
        surface_kind = input_payload.get("surface_kind")
        if isinstance(repo_name, str) and isinstance(surface_kind, str):
            actual_inputs.append((repo_name, surface_kind))
    if tuple(actual_inputs) != RPG_NAVIGATION_REQUIRED_INPUTS:
        issues.append(
            ValidationIssue(
                RPG_NAVIGATION_EXAMPLE_NAME,
                "inputs must stay ordered as playbook quest_dispatch, playbook party_template_cards, and eval unlock_proof_cards",
            )
        )

    for index, raw_entry in enumerate(entries):
        location = f"{RPG_NAVIGATION_EXAMPLE_NAME}.entries[{index}]"
        try:
            entry = ensure_mapping(raw_entry, location)
        except RouterError as exc:
            issues.append(ValidationIssue(RPG_NAVIGATION_EXAMPLE_NAME, str(exc)))
            continue
        actions = entry.get("entry_actions")
        if actions != EXPECTED_QUEST_HINT_ACTION_ORDER:
            issues.append(
                ValidationIssue(
                    RPG_NAVIGATION_EXAMPLE_NAME,
                    f"{location}.entry_actions must stay exactly {EXPECTED_QUEST_HINT_ACTION_ORDER}",
                )
            )

    example_text = example_path.read_text(encoding="utf-8")
    if "AOA-PB-Q-0004" in example_text:
        issues.append(
            ValidationIssue(
                RPG_NAVIGATION_EXAMPLE_NAME,
                "example must not keep legacy playbook quest id 'AOA-PB-Q-0004'",
            )
        )
    if '"repo": "aoa-routing"' in example_text and '"surface_kind": "quest_dispatch"' in example_text:
        issues.append(
            ValidationIssue(
                RPG_NAVIGATION_EXAMPLE_NAME,
                "example must not pretend aoa-routing owns quest_dispatch source inputs",
            )
        )


def validate_local_questbook_surfaces(repo_root: Path, issues: list[ValidationIssue]) -> None:
    questbook_path = repo_root / "QUESTBOOK.md"
    seam_path = repo_root / "docs" / "QUEST_ROUTING_SEAM.md"
    schema_path = repo_root / "schemas" / "quest_dispatch_hint.schema.json"
    quests_dir = repo_root / "quests"

    try:
        questbook_text = questbook_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(ValidationIssue(repo_relative(repo_root, questbook_path), "missing required file"))
        return

    try:
        seam_text = seam_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(ValidationIssue(repo_relative(repo_root, seam_path), "missing required file"))
        return

    try:
        schema_payload = load_json_file(schema_path)
        schema_object = ensure_mapping(schema_payload, repo_relative(repo_root, schema_path))
    except RouterError as exc:
        issues.append(ValidationIssue(repo_relative(repo_root, schema_path), str(exc)))
        schema_object = None
    if schema_object is not None:
        missing = [key for key in REQUIRED_QUEST_SCHEMA_TOP_LEVEL_KEYS if key not in schema_object]
        if missing:
            issues.append(
                ValidationIssue(
                    repo_relative(repo_root, schema_path),
                    f"schema is missing required top-level keys: {', '.join(missing)}",
                )
            )
        else:
            try:
                properties = ensure_mapping(
                    schema_object["properties"],
                    repo_relative(repo_root, schema_path),
                )
            except RouterError as exc:
                issues.append(
                    ValidationIssue(repo_relative(repo_root, schema_path), str(exc))
                )
            else:
                schema_version = properties.get("schema_version", {})
                if not isinstance(schema_version, dict) or schema_version.get("const") != "quest_dispatch_hint_v2":
                    issues.append(
                        ValidationIssue(
                            repo_relative(repo_root, schema_path),
                            "schema must constrain properties.schema_version.const to 'quest_dispatch_hint_v2'",
                        )
                    )
        try:
            Draft202012Validator.check_schema(schema_object)
        except SchemaError as exc:
            issues.append(ValidationIssue(repo_relative(repo_root, schema_path), f"invalid JSON schema: {exc.message}"))

    actual_ids = discover_routing_quest_ids(repo_root)
    missing_foundation = [
        quest_id for quest_id in FOUNDATION_ROUTING_QUEST_IDS if quest_id not in actual_ids
    ]
    if missing_foundation:
        issues.append(
            ValidationIssue(
                "quests",
                "routing quest set must include the foundation quests (missing: "
                + ", ".join(missing_foundation)
                + ")",
            )
        )

    for quest_id in actual_ids:
        payload = load_yaml_mapping(quests_dir / f"{quest_id}.yaml", issues, repo_root=repo_root)
        if payload is None:
            continue
        if payload.get("schema_version") != "work_quest_v1":
            issues.append(
                ValidationIssue(
                    f"quests/{quest_id}.yaml",
                    f"unsupported schema_version '{payload.get('schema_version')}'",
                )
            )
        if payload.get("repo") != "aoa-routing":
            issues.append(ValidationIssue(f"quests/{quest_id}.yaml", "quest must target repo 'aoa-routing'"))
        if payload.get("id") != quest_id:
            issues.append(ValidationIssue(f"quests/{quest_id}.yaml", f"id must match filename '{quest_id}'"))
        if payload.get("public_safe") is not True:
            issues.append(ValidationIssue(f"quests/{quest_id}.yaml", "quest must set public_safe: true"))
        expected_state = EXPECTED_ROUTING_QUEST_STATES.get(quest_id)
        if expected_state is not None and payload.get("state") != expected_state:
            issues.append(
                ValidationIssue(
                    f"quests/{quest_id}.yaml",
                    f"quest state must stay '{expected_state}' in the current routing wave",
                )
            )
        if expected_state in {"done", "dropped"}:
            if quest_id in questbook_text:
                issues.append(
                    ValidationIssue(
                        "QUESTBOOK.md",
                        f"closed quest id '{quest_id}' must not stay in the active human questbook",
                    )
                )
        else:
            if quest_id not in questbook_text:
                issues.append(
                    ValidationIssue(
                        "QUESTBOOK.md",
                        f"active or reanchored quest id '{quest_id}' must stay visible in QUESTBOOK.md",
                    )
                )
        if quest_id == "AOA-RT-Q-0002":
            notes = payload.get("notes")
            if not isinstance(notes, str) or REQUIRED_REANCHOR_NOTE_SNIPPET not in notes:
                issues.append(
                    ValidationIssue(
                        f"quests/{quest_id}.yaml",
                        "reanchored quest must record the current lack of live frontier d0/d1 r0/r1 leaves",
                    )
                )
        if quest_id == "AOA-RT-Q-0003":
            validate_adjunct_quest_board_surface(repo_root, issues)
        if quest_id == "AOA-RT-Q-0004":
            validate_rpg_navigation_bridge_surface(repo_root, issues)

    if "## Blocked / reanchor" not in questbook_text:
        issues.append(
            ValidationIssue(
                "QUESTBOOK.md",
                "QUESTBOOK.md must keep a 'Blocked / reanchor' bucket in the first live routing wave",
            )
        )

    for snippet in REQUIRED_ROUTING_SEAM_SNIPPETS:
        if snippet not in seam_text:
            issues.append(
                ValidationIssue(
                    "docs/QUEST_ROUTING_SEAM.md",
                    "QUEST routing seam must refuse live quest authority and name generated-only ingestion",
                )
            )


def validate_quest_dispatch_hints(
    quest_dispatch_hints_payload: dict[str, Any],
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    federation_payload: dict[str, Any],
    issues: list[ValidationIssue],
) -> None:
    source_roots = {
        "aoa-techniques": techniques_root.resolve(),
        "aoa-skills": skills_root.resolve(),
        "aoa-evals": evals_root.resolve(),
    }
    try:
        source_inputs = ensure_list(
            quest_dispatch_hints_payload.get("source_inputs"),
            "quest_dispatch_hints.min.json.source_inputs",
        )
        actions_enabled = ensure_string_list(
            quest_dispatch_hints_payload.get("actions_enabled"),
            "quest_dispatch_hints.min.json.actions_enabled",
        )
        hints = ensure_list(
            quest_dispatch_hints_payload.get("hints"),
            "quest_dispatch_hints.min.json.hints",
        )
        federation_entries = ensure_list(
            federation_payload.get("entrypoints"),
            "federation_entrypoints.min.json.entrypoints",
        )
    except RouterError as exc:
        issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
        return

    if quest_dispatch_hints_payload.get("wave_scope") != QUEST_ROUTING_WAVE_SCOPE:
        issues.append(
            ValidationIssue(
                "quest_dispatch_hints.min.json",
                f"wave_scope must stay '{QUEST_ROUTING_WAVE_SCOPE}' in the first live routing wave",
            )
        )
    if actions_enabled != list(QUEST_ROUTING_ACTIONS_ENABLED):
        issues.append(
            ValidationIssue(
                "quest_dispatch_hints.min.json",
                "actions_enabled must stay exactly ['inspect', 'expand', 'handoff']",
            )
        )

    expected_source_inputs = build_quest_routing_source_inputs()
    if source_inputs != expected_source_inputs:
        issues.append(
            ValidationIssue(
                "quest_dispatch_hints.min.json",
                "source_inputs must list only the live source/proof quest catalog and dispatch surfaces in repo order",
            )
        )

    tier_ids: set[str] = set()
    for index, raw_entry in enumerate(federation_entries):
        location = f"federation_entrypoints.min.json.entrypoints[{index}]"
        try:
            entry = ensure_mapping(raw_entry, location)
        except RouterError as exc:
            issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))
            continue
        if entry.get("kind") == "tier":
            try:
                tier_ids.add(ensure_string(entry.get("id"), f"{location}.id"))
            except RouterError as exc:
                issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))

    catalog_index_by_repo: dict[str, dict[str, dict[str, Any]]] = {}
    dispatch_index_by_repo: dict[str, dict[str, dict[str, Any]]] = {}
    eligible_hint_keys: set[tuple[str, str]] = set()
    tiny_safe_frontier_exists = False
    for repo_name in QUEST_ROUTING_SOURCE_REPOS:
        try:
            catalog_entries, dispatch_entries = load_live_quest_projection_entries(
                source_roots[repo_name],
                repo_name,
            )
        except RouterError as exc:
            issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
            return
        catalog_index: dict[str, dict[str, Any]] = {}
        dispatch_index: dict[str, dict[str, Any]] = {}
        for index, raw_entry in enumerate(catalog_entries):
            location = f"{repo_name}/generated/quest_catalog.min.json[{index}]"
            try:
                entry = ensure_mapping(raw_entry, location)
                quest_id = ensure_string(entry.get("id"), f"{location}.id")
            except RouterError as exc:
                issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
                continue
            catalog_index[quest_id] = entry
        for index, raw_entry in enumerate(dispatch_entries):
            location = f"{repo_name}/generated/quest_dispatch.min.json[{index}]"
            try:
                entry = ensure_mapping(raw_entry, location)
                quest_id = ensure_string(entry.get("id"), f"{location}.id")
                state = ensure_string(entry.get("state"), f"{location}.state")
                band = ensure_string(entry.get("band"), f"{location}.band")
                difficulty = ensure_string(entry.get("difficulty"), f"{location}.difficulty")
                risk = ensure_string(entry.get("risk"), f"{location}.risk")
                public_safe = entry.get("public_safe")
                if public_safe is not True:
                    continue
                if state in QUEST_ROUTING_CLOSED_STATES:
                    continue
            except RouterError as exc:
                issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
                continue
            dispatch_index[quest_id] = entry
            eligible_hint_keys.add((repo_name, quest_id))
            if band == "frontier" and difficulty in {"d0_probe", "d1_patch"} and risk in {
                "r0_readonly",
                "r1_repo_local",
            }:
                tiny_safe_frontier_exists = True
        catalog_index_by_repo[repo_name] = catalog_index
        dispatch_index_by_repo[repo_name] = dispatch_index

    if tiny_safe_frontier_exists:
        issues.append(
            ValidationIssue(
                "quest_dispatch_hints.min.json",
                "AOA-RT-Q-0002 must not remain reanchored once live frontier d0/d1 r0/r1 leaves exist",
            )
        )

    seen_hint_keys: set[tuple[str, str]] = set()
    for index, raw_hint in enumerate(hints):
        location = f"quest_dispatch_hints.min.json.hints[{index}]"
        try:
            hint = ensure_mapping(raw_hint, location)
        except RouterError as exc:
            issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
            continue
        validate_against_schema(hint, "quest_dispatch_hint.schema.json", location, issues)
        try:
            repo_name = ensure_string(hint.get("repo"), f"{location}.repo")
            quest_id = ensure_string(hint.get("id"), f"{location}.id")
            state = ensure_string(hint.get("state"), f"{location}.state")
            band = ensure_string(hint.get("band"), f"{location}.band")
            difficulty = ensure_string(hint.get("difficulty"), f"{location}.difficulty")
            risk = ensure_string(hint.get("risk"), f"{location}.risk")
            delegate_tier = ensure_string(
                hint.get("delegate_tier"),
                f"{location}.delegate_tier",
            )
            source_path = ensure_repo_relative_path(
                hint.get("source_path"),
                f"{location}.source_path",
            )
            public_safe = ensure_bool(hint.get("public_safe"), f"{location}.public_safe")
        except RouterError as exc:
            issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
            continue

        if repo_name not in source_roots:
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    f"{location}.repo must stay within the first live source-only wave",
                )
            )
            continue
        if repo_name == "Dionysus":
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    "Dionysus quests must stay out of the first live source-only routing wave",
                )
            )
        if state in QUEST_ROUTING_CLOSED_STATES:
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    f"{location}.state must not include closed quests in live routing hints",
                )
            )
        if public_safe is not True:
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    f"{location}.public_safe must stay true for routed quest hints",
                )
            )

        catalog_entry = catalog_index_by_repo[repo_name].get(quest_id)
        dispatch_entry = dispatch_index_by_repo[repo_name].get(quest_id)
        if catalog_entry is None or dispatch_entry is None:
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    f"{location} must point to a live non-closed quest from {repo_name}",
                )
            )
            continue
        for key, expected_value in (
            ("repo", repo_name),
            ("state", dispatch_entry.get("state")),
            ("band", dispatch_entry.get("band")),
            ("difficulty", dispatch_entry.get("difficulty")),
            ("risk", dispatch_entry.get("risk")),
            ("delegate_tier", dispatch_entry.get("delegate_tier")),
            ("source_path", dispatch_entry.get("source_path")),
            ("public_safe", dispatch_entry.get("public_safe")),
        ):
            actual_value = hint.get(key)
            if actual_value != expected_value:
                issues.append(
                    ValidationIssue(
                        "quest_dispatch_hints.min.json",
                        f"{location}.{key} must stay aligned with {repo_name}/generated/quest_dispatch.min.json",
                    )
                )
        if quest_id not in catalog_index_by_repo[repo_name]:
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    f"{location}.id must exist in {repo_name}/generated/quest_catalog.min.json",
                )
            )
        seen_hint_keys.add((repo_name, quest_id))

        try:
            next_actions = ensure_list(hint.get("next_actions"), f"{location}.next_actions")
        except RouterError as exc:
            issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
            next_actions = []
        if len(next_actions) != len(EXPECTED_QUEST_HINT_ACTION_ORDER):
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    f"{location}.next_actions must publish exactly three bounded actions",
                )
            )
        for action_index, expected_verb in enumerate(EXPECTED_QUEST_HINT_ACTION_ORDER):
            if action_index >= len(next_actions):
                continue
            action_location = f"{location}.next_actions[{action_index}]"
            try:
                action = ensure_mapping(next_actions[action_index], action_location)
                verb = ensure_string(action.get("verb"), f"{action_location}.verb")
                target_repo = ensure_string(
                    action.get("target_repo"),
                    f"{action_location}.target_repo",
                )
                target_surface = ensure_repo_relative_path(
                    action.get("target_surface"),
                    f"{action_location}.target_surface",
                )
                match_key = ensure_string(
                    action.get("match_key"),
                    f"{action_location}.match_key",
                )
                target_value = ensure_string(
                    action.get("target_value"),
                    f"{action_location}.target_value",
                )
            except RouterError as exc:
                issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
                continue
            if verb != expected_verb:
                issues.append(
                    ValidationIssue(
                        "quest_dispatch_hints.min.json",
                        f"{action_location}.verb must stay '{expected_verb}'",
                    )
                )
            if target_surface.endswith(".example.json") or target_surface.startswith("quests/"):
                issues.append(
                    ValidationIssue(
                        "quest_dispatch_hints.min.json",
                        f"{action_location}.target_surface must stay on live generated surfaces or source docs, never example fixtures or live quest YAML",
                    )
                )
            if expected_verb == "inspect":
                if (
                    target_repo != repo_name
                    or target_surface != "generated/quest_dispatch.min.json"
                    or match_key != "id"
                    or target_value != quest_id
                ):
                    issues.append(
                        ValidationIssue(
                            "quest_dispatch_hints.min.json",
                            f"{action_location} must inspect the owning repo live quest dispatch surface",
                        )
                    )
            elif expected_verb == "expand":
                expected_surface = QUEST_ROUTING_EXPAND_DOC_BY_REPO[repo_name]
                expected_path = source_roots[repo_name] / expected_surface
                if (
                    target_repo != repo_name
                    or target_surface != expected_surface
                    or match_key != "path"
                    or target_value != expected_surface
                ):
                    issues.append(
                        ValidationIssue(
                            "quest_dispatch_hints.min.json",
                            f"{action_location} must expand to the repo-local quest integration note",
                        )
                    )
                if not expected_path.exists():
                    issues.append(
                        ValidationIssue(
                            "quest_dispatch_hints.min.json",
                            f"{repo_name}/{expected_surface} is missing",
                        )
                    )
            elif expected_verb == "handoff":
                if (
                    target_repo != "aoa-routing"
                    or target_surface != FEDERATION_ENTRYPOINTS_FILE
                    or match_key != "id"
                ):
                    issues.append(
                        ValidationIssue(
                            "quest_dispatch_hints.min.json",
                            f"{action_location} must hand off through aoa-routing/{FEDERATION_ENTRYPOINTS_FILE}",
                        )
                    )
                if target_value != delegate_tier:
                    issues.append(
                        ValidationIssue(
                            "quest_dispatch_hints.min.json",
                            f"{action_location}.target_value must stay aligned with delegate_tier",
                        )
                    )
                if target_value not in tier_ids:
                    issues.append(
                        ValidationIssue(
                            "quest_dispatch_hints.min.json",
                            f"{action_location}.target_value references unknown federation tier '{target_value}'",
                        )
                    )

        fallback_location = f"{location}.fallback"
        try:
            fallback = ensure_mapping(hint.get("fallback"), fallback_location)
            fallback_verb = ensure_string(fallback.get("verb"), f"{fallback_location}.verb")
            fallback_repo = ensure_string(fallback.get("target_repo"), f"{fallback_location}.target_repo")
            fallback_surface = ensure_repo_relative_path(
                fallback.get("target_surface"),
                f"{fallback_location}.target_surface",
            )
            fallback_match_key = ensure_string(
                fallback.get("match_key"),
                f"{fallback_location}.match_key",
            )
            fallback_target_value = ensure_string(
                fallback.get("target_value"),
                f"{fallback_location}.target_value",
            )
        except RouterError as exc:
            issues.append(ValidationIssue("quest_dispatch_hints.min.json", str(exc)))
            continue
        if fallback_surface.endswith(".example.json") or fallback_surface.startswith("quests/"):
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    f"{fallback_location}.target_surface must stay on live generated catalog surfaces",
                )
            )
        if (
            fallback_verb != "inspect"
            or fallback_repo != repo_name
            or fallback_surface != "generated/quest_catalog.min.json"
            or fallback_match_key != "id"
            or fallback_target_value != quest_id
        ):
            issues.append(
                ValidationIssue(
                    "quest_dispatch_hints.min.json",
                    f"{fallback_location} must point back to the owning repo live quest catalog surface",
                )
            )

    if seen_hint_keys != eligible_hint_keys:
        missing = sorted(f"{repo}:{quest_id}" for repo, quest_id in (eligible_hint_keys - seen_hint_keys))
        extra = sorted(f"{repo}:{quest_id}" for repo, quest_id in (seen_hint_keys - eligible_hint_keys))
        details: list[str] = []
        if missing:
            details.append(f"missing hints: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected hints: {', '.join(extra)}")
        issues.append(
            ValidationIssue(
                "quest_dispatch_hints.min.json",
                f"live quest routing hints must match the current non-closed source/proof quest set ({'; '.join(details)})",
            )
        )


def validate_rebuild_parity(
    outputs: dict[str, Any],
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
    agents_root: Path,
    aoa_root: Path,
    playbooks_root: Path,
    kag_root: Path,
    tos_root: Path,
    issues: list[ValidationIssue],
) -> None:
    try:
        expected_outputs = build_outputs(
            techniques_root.resolve(),
            skills_root.resolve(),
            evals_root.resolve(),
            memo_root.resolve(),
            agents_root.resolve(),
            aoa_root.resolve(),
            playbooks_root.resolve(),
            kag_root.resolve(),
            tos_root.resolve(),
        )
    except RouterError as exc:
        issues.append(
            ValidationIssue(
                "generated",
                f"could not rebuild canonical outputs from current sibling catalogs: {exc}",
            )
        )
        return

    for filename, expected_payload in expected_outputs.items():
        actual_payload = outputs.get(filename)
        if actual_payload is not None and actual_payload != expected_payload:
            issues.append(
                ValidationIssue(
                    filename,
                    "published output does not match the canonical rebuild from current sibling catalogs",
                )
            )


def validate_entry_repo_and_path(
    entry: dict[str, Any],
    location: str,
    issues: list[ValidationIssue],
) -> None:
    kind = entry.get("kind")
    if not isinstance(kind, str):
        return

    repo = entry.get("repo")
    expected_repo = CANONICAL_REPO_BY_KIND.get(kind)
    if expected_repo is not None and repo != expected_repo:
        issues.append(
            ValidationIssue(
                location,
                f"{kind} entries must use canonical repo '{expected_repo}'",
            )
        )

    try:
        ensure_repo_relative_path(entry.get("path"), f"{location}.path")
    except RouterError as exc:
        issues.append(ValidationIssue(location, str(exc)))


def validate_registry_entry_attributes(
    entry: dict[str, Any],
    location: str,
    issues: list[ValidationIssue],
) -> bool:
    attributes = entry.get("attributes")
    if not isinstance(attributes, dict):
        issues.append(ValidationIssue(location, "attributes must be an object"))
        return False

    kind = entry.get("kind")
    if not isinstance(kind, str):
        return False

    if kind == "technique":
        expected_keys = {
            "domain",
            "maturity_score",
            "rigor_level",
            "reversibility",
            "review_required",
            "validation_strength",
            "export_ready",
        }
        if set(attributes) != expected_keys:
            issues.append(ValidationIssue(location, "technique attributes do not match the expected shape"))
            return False
        if not isinstance(attributes["domain"], str):
            issues.append(ValidationIssue(location, "technique domain must be a string"))
        if not isinstance(attributes["maturity_score"], int):
            issues.append(ValidationIssue(location, "technique maturity_score must be an integer"))
        for key in ("rigor_level", "reversibility", "validation_strength"):
            if not isinstance(attributes[key], str):
                issues.append(ValidationIssue(location, f"technique {key} must be a string"))
        for key in ("review_required", "export_ready"):
            if not isinstance(attributes[key], bool):
                issues.append(ValidationIssue(location, f"technique {key} must be a boolean"))
        return True

    if kind == "skill":
        expected_keys = {"scope", "invocation_mode", "technique_dependencies"}
        if set(attributes) != expected_keys:
            issues.append(ValidationIssue(location, "skill attributes do not match the expected shape"))
            return False
        for key in ("scope", "invocation_mode"):
            if not isinstance(attributes[key], str):
                issues.append(ValidationIssue(location, f"skill {key} must be a string"))
        try:
            ensure_string_list(attributes["technique_dependencies"], f"{location}.technique_dependencies")
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            return False
        return True

    if kind == "eval":
        expected_keys = {
            "category",
            "object_under_evaluation",
            "claim_type",
            "baseline_mode",
            "verdict_shape",
            "review_required",
            "validation_strength",
            "export_ready",
            "technique_dependencies",
            "skill_dependencies",
        }
        if set(attributes) != expected_keys:
            issues.append(ValidationIssue(location, "eval attributes do not match the expected shape"))
            return False
        for key in (
            "category",
            "object_under_evaluation",
            "claim_type",
            "baseline_mode",
            "verdict_shape",
            "validation_strength",
        ):
            if not isinstance(attributes[key], str):
                issues.append(ValidationIssue(location, f"eval {key} must be a string"))
        for key in ("review_required", "export_ready"):
            if not isinstance(attributes[key], bool):
                issues.append(ValidationIssue(location, f"eval {key} must be a boolean"))
        try:
            ensure_string_list(attributes["technique_dependencies"], f"{location}.technique_dependencies")
            ensure_string_list(attributes["skill_dependencies"], f"{location}.skill_dependencies")
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            return False
        return True

    if kind == "memo":
        expected_keys = {
            "surface_kind",
            "primary_focus",
            "recall_modes",
            "temperature",
            "inspect_surface",
            "expand_surface",
        }
        if set(attributes) != expected_keys:
            issues.append(ValidationIssue(location, "memo attributes do not match the expected shape"))
            return False
        for key in ("surface_kind", "primary_focus", "temperature", "inspect_surface", "expand_surface"):
            if not isinstance(attributes[key], str):
                issues.append(ValidationIssue(location, f"memo {key} must be a string"))
        try:
            ensure_string_list(attributes["recall_modes"], f"{location}.recall_modes")
            ensure_repo_relative_path(attributes["inspect_surface"], f"{location}.inspect_surface")
            ensure_repo_relative_path(attributes["expand_surface"], f"{location}.expand_surface")
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            return False
        return True

    issues.append(ValidationIssue(location, f"unsupported entry kind '{kind}'"))
    return False


def registry_entry_key(entry: dict[str, Any]) -> tuple[str, str] | None:
    kind = entry.get("kind")
    identifier = entry.get("id")
    if not isinstance(kind, str) or not isinstance(identifier, str):
        return None
    return kind, identifier


def is_projection_safe_registry_entry(entry: dict[str, Any]) -> bool:
    key = registry_entry_key(entry)
    if key is None or key[0] not in ALL_KINDS:
        return False
    return all(
        isinstance(entry.get(field), str)
        for field in ("name", "repo", "path", "status", "summary")
    )


def validate_registry_dependencies(
    registry_entries: list[dict[str, Any]],
    dependency_entries: list[dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    entries_by_kind: dict[str, set[str]] = {kind: set() for kind in ACTIVE_KINDS}
    for entry in registry_entries:
        key = registry_entry_key(entry)
        if key is None:
            continue
        kind, identifier = key
        if kind in entries_by_kind:
            entries_by_kind[kind].add(identifier)

    for entry in dependency_entries:
        key = registry_entry_key(entry)
        if key is None:
            continue
        kind, identifier = key
        location = f"cross_repo_registry.min.json:{kind}:{identifier}"
        attributes = entry.get("attributes")
        if not isinstance(attributes, dict):
            continue
        if kind == "skill":
            for dependency_id in attributes.get("technique_dependencies", []):
                if is_pending_technique_id(dependency_id):
                    continue
                if dependency_id not in entries_by_kind["technique"]:
                    issues.append(
                        ValidationIssue(location, f"unresolved technique dependency '{dependency_id}'")
                    )
        elif kind == "eval":
            for dependency_id in attributes.get("technique_dependencies", []):
                if is_pending_technique_id(dependency_id):
                    continue
                if dependency_id not in entries_by_kind["technique"]:
                    issues.append(
                        ValidationIssue(location, f"unresolved technique dependency '{dependency_id}'")
                    )
            for dependency_name in attributes.get("skill_dependencies", []):
                if dependency_name not in entries_by_kind["skill"]:
                    issues.append(
                        ValidationIssue(location, f"unresolved skill dependency '{dependency_name}'")
                    )


def capsule_array_key(kind: str) -> str:
    if kind == "technique":
        return "techniques"
    if kind == "skill":
        return "skills"
    if kind == "eval":
        return "evals"
    if kind == "memo":
        return "memo_surfaces"
    raise RouterError(f"capsule surfaces do not support kind '{kind}'")


def section_array_key(kind: str) -> str:
    if kind == "technique":
        return "techniques"
    if kind == "skill":
        return "skills"
    if kind == "eval":
        return "evals"
    if kind == "memo":
        return "memo_surfaces"
    raise RouterError(f"section surfaces do not support kind '{kind}'")


def section_content_field(kind: str) -> str:
    if kind == "memo":
        return "body"
    return "content_markdown"


def validate_inspect_targets(
    registry_entries: list[dict[str, Any]],
    hints_payload: dict[str, Any],
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
    issues: list[ValidationIssue],
) -> None:
    source_roots = {
        "aoa-techniques": techniques_root.resolve(),
        "aoa-skills": skills_root.resolve(),
        "aoa-evals": evals_root.resolve(),
        "aoa-memo": memo_root.resolve(),
    }
    try:
        hints = ensure_list(hints_payload.get("hints"), "task_to_surface_hints.json.hints")
    except RouterError as exc:
        issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
        return
    for index, raw_hint in enumerate(hints):
        try:
            hint = ensure_mapping(raw_hint, f"task_to_surface_hints.json.hints[{index}]")
        except RouterError as exc:
            issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
            continue
        kind = hint.get("kind")
        enabled = hint.get("enabled")
        if not isinstance(kind, str) or kind not in ALL_KINDS:
            continue
        if not isinstance(enabled, bool):
            continue
        if not enabled:
            continue
        actions = hint.get("actions")
        if not isinstance(actions, dict):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"hint for kind '{kind}' must define actions",
                )
            )
            continue
        inspect = actions.get("inspect")
        if not isinstance(inspect, dict) or not inspect.get("enabled"):
            continue
        source_repo = hint.get("source_repo")
        if not isinstance(source_repo, str) or source_repo not in source_roots:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"hint for kind '{kind}' has an invalid source_repo",
                )
            )
            continue
        source_root = source_roots[source_repo]
        surface_file = inspect.get("surface_file")
        match_field = inspect.get("match_field")
        if not isinstance(surface_file, str) or not surface_file.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled inspect action for kind '{kind}' must define surface_file",
                )
            )
            continue
        if not isinstance(match_field, str) or not match_field.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled inspect action for kind '{kind}' must define match_field",
                )
            )
            continue
        surface_path = source_root / surface_file
        location = f"{source_repo}/{surface_file}"
        try:
            payload = ensure_mapping(load_json_file(surface_path), location)
            entries = ensure_list(payload.get(capsule_array_key(kind)), location)
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            continue

        seen_matches: set[str] = set()
        for index, raw_entry in enumerate(entries):
            entry_location = f"{location}[{index}]"
            try:
                capsule_entry = ensure_mapping(raw_entry, entry_location)
                match_value = capsule_entry.get(match_field)
                if not isinstance(match_value, str) or not match_value.strip():
                    raise RouterError(f"{entry_location}.{match_field} must be a non-empty string")
            except RouterError as exc:
                issues.append(ValidationIssue(location, str(exc)))
                continue
            if match_value in seen_matches:
                issues.append(
                        ValidationIssue(
                            location,
                            f"duplicate inspect match '{match_value}' for kind '{kind}'",
                        )
                    )
            seen_matches.add(match_value)

        expected_matches = {
            entry["id"] if match_field == "id" else entry["name"]
            for entry in registry_entries
            if entry["kind"] == kind
        }
        missing_matches = sorted(expected_matches - seen_matches)
        for match_value in missing_matches:
            issues.append(
                ValidationIssue(
                    location,
                    f"inspect surface is missing {kind} match '{match_value}'",
                )
            )
        unexpected_matches = sorted(seen_matches - expected_matches)
        for match_value in unexpected_matches:
            issues.append(
                ValidationIssue(
                    location,
                    f"inspect surface contains unexpected {kind} match '{match_value}'",
                )
            )


def validate_expand_targets(
    registry_entries: list[dict[str, Any]],
    hints_payload: dict[str, Any],
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
    issues: list[ValidationIssue],
) -> None:
    source_roots = {
        "aoa-techniques": techniques_root.resolve(),
        "aoa-skills": skills_root.resolve(),
        "aoa-evals": evals_root.resolve(),
        "aoa-memo": memo_root.resolve(),
    }
    try:
        hints = ensure_list(hints_payload.get("hints"), "task_to_surface_hints.json.hints")
    except RouterError as exc:
        issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
        return
    for index, raw_hint in enumerate(hints):
        try:
            hint = ensure_mapping(raw_hint, f"task_to_surface_hints.json.hints[{index}]")
        except RouterError as exc:
            issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
            continue
        kind = hint.get("kind")
        enabled = hint.get("enabled")
        if not isinstance(kind, str) or kind not in ALL_KINDS:
            continue
        if not isinstance(enabled, bool):
            continue
        if not enabled:
            continue
        actions = hint.get("actions")
        if not isinstance(actions, dict):
            continue
        expand = actions.get("expand")
        if not isinstance(expand, dict) or not expand.get("enabled"):
            continue
        source_repo = hint.get("source_repo")
        if not isinstance(source_repo, str) or source_repo not in source_roots:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"hint for kind '{kind}' has an invalid source_repo",
                )
            )
            continue
        source_root = source_roots[source_repo]
        surface_file = expand.get("surface_file")
        match_field = expand.get("match_field")
        section_key_field = expand.get("section_key_field")
        default_sections = expand.get("default_sections")
        supported_sections = expand.get("supported_sections")
        if not isinstance(surface_file, str) or not surface_file.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{kind}' must define surface_file",
                )
            )
            continue
        if not isinstance(match_field, str) or not match_field.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{kind}' must define match_field",
                )
            )
            continue
        if not isinstance(section_key_field, str) or not section_key_field.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{kind}' must define section_key_field",
                )
            )
            continue
        if not isinstance(default_sections, list) or not all(
            isinstance(section, str) and section.strip() for section in default_sections
        ):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{kind}' must define default_sections as a string list",
                )
            )
            continue
        if not isinstance(supported_sections, list) or not all(
            isinstance(section, str) and section.strip() for section in supported_sections
        ):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{kind}' must define supported_sections as a string list",
                )
            )
            continue
        location = f"{source_repo}/{surface_file}"
        surface_path = source_root / surface_file
        try:
            payload = ensure_mapping(load_json_file(surface_path), location)
            entries = ensure_list(payload.get(section_array_key(kind)), location)
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            continue

        section_keys_by_match: dict[str, list[str]] = {}
        seen_matches: set[str] = set()
        for index, raw_entry in enumerate(entries):
            entry_location = f"{location}[{index}]"
            try:
                section_entry = ensure_mapping(raw_entry, entry_location)
                match_value = section_entry.get(match_field)
                if not isinstance(match_value, str) or not match_value.strip():
                    raise RouterError(f"{entry_location}.{match_field} must be a non-empty string")
                sections = ensure_list(section_entry.get("sections"), f"{entry_location}.sections")
            except RouterError as exc:
                issues.append(ValidationIssue(location, str(exc)))
                continue
            if match_value in seen_matches:
                issues.append(
                        ValidationIssue(
                            location,
                            f"duplicate expand match '{match_value}' for kind '{kind}'",
                        )
                    )
            seen_matches.add(match_value)

            section_keys: list[str] = []
            for section_index, raw_section in enumerate(sections):
                section_location = f"{entry_location}.sections[{section_index}]"
                try:
                    section = ensure_mapping(raw_section, section_location)
                    section_key = section.get(section_key_field)
                    if not isinstance(section_key, str) or not section_key.strip():
                        raise RouterError(
                            f"{section_location}.{section_key_field} must be a non-empty string"
                        )
                    heading = section.get("heading")
                    content_field = section_content_field(kind)
                    content_markdown = section.get(content_field)
                    if not isinstance(heading, str) or not heading.strip():
                        raise RouterError(f"{section_location}.heading must be a non-empty string")
                    if not isinstance(content_markdown, str) or not content_markdown.strip():
                        raise RouterError(
                            f"{section_location}.{content_field} must be a non-empty string"
                        )
                except RouterError as exc:
                    issues.append(ValidationIssue(location, str(exc)))
                    continue
                section_keys.append(section_key)

            if len(section_keys) != len(set(section_keys)):
                issues.append(
                        ValidationIssue(
                            location,
                            f"expand surface contains duplicate section keys for {kind} match '{match_value}'",
                        )
                )
            section_keys_by_match[match_value] = section_keys

        expected_matches = {
            entry["id"] if match_field == "id" else entry["name"]
            for entry in registry_entries
            if entry["kind"] == kind
        }
        missing_matches = sorted(expected_matches - seen_matches)
        for match_value in missing_matches:
            issues.append(
                ValidationIssue(
                    location,
                    f"expand surface is missing {kind} match '{match_value}'",
                )
            )
        unexpected_matches = sorted(seen_matches - expected_matches)
        for match_value in unexpected_matches:
            issues.append(
                ValidationIssue(
                    location,
                    f"expand surface contains unexpected {kind} match '{match_value}'",
                )
            )

        if any(section not in supported_sections for section in default_sections):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"default expand sections for kind '{kind}' must be a subset of supported_sections",
                )
            )

        supported_tuple = tuple(supported_sections)
        default_tuple = tuple(default_sections)
        if not supported_tuple:
            continue
        for match_value in sorted(expected_matches & seen_matches):
            actual_keys = tuple(section_keys_by_match.get(match_value, []))
            if actual_keys != supported_tuple:
                issues.append(
                        ValidationIssue(
                            location,
                            f"expand surface for {kind} match '{match_value}' must expose the supported section order",
                        )
                    )
                continue
            missing_defaults = [section for section in default_tuple if section not in actual_keys]
            if missing_defaults:
                issues.append(
                        ValidationIssue(
                            location,
                            f"expand surface for {kind} match '{match_value}' is missing default sections: {', '.join(missing_defaults)}",
                        )
                    )


def load_surface_entries_for_validation(
    payload: dict[str, Any],
    surface_file: str,
) -> list[dict[str, Any]]:
    if Path(surface_file).name == Path(FEDERATION_ENTRYPOINTS_FILE).name:
        root_entries = ensure_list(
            payload.get("root_entries"),
            f"{surface_file}.root_entries",
        )
        entrypoints = ensure_list(
            payload.get("entrypoints"),
            f"{surface_file}.entrypoints",
        )
        return root_entries + entrypoints
    if Path(surface_file).name == Path(TOS_TINY_ENTRY_ROUTE_PATH).name:
        return [ensure_mapping(payload, surface_file)]
    array_key_by_filename = {
        "aoa_router.min.json": "entries",
        "task_to_surface_hints.json": "hints",
        "pairing_hints.min.json": "entries",
        Path(TOS_ROUTE_RETRIEVAL_SURFACE_REF).name: "routes",
        "repo_doc_surface_manifest.min.json": "docs",
        "technique_capsules.json": "techniques",
        "technique_catalog.json": "techniques",
        "technique_catalog.min.json": "techniques",
        "skill_capsules.json": "skills",
        "eval_capsules.json": "evals",
        "memory_catalog.min.json": "memo_surfaces",
        "memory_capsules.json": "memo_surfaces",
        "memory_object_catalog.min.json": "memory_objects",
        "memory_object_capsules.json": "memory_objects",
        "technique_sections.full.json": "techniques",
        "skill_sections.full.json": "skills",
        "eval_sections.full.json": "evals",
        "memory_sections.full.json": "memo_surfaces",
        "memory_object_sections.full.json": "memory_objects",
    }
    key = array_key_by_filename.get(Path(surface_file).name)
    if key is None:
        raise RouterError(f"unsupported surface file '{surface_file}' for validation lookup")
    return ensure_list(payload.get(key), f"{surface_file}.{key}")


def resolve_routing_surface_path(relative_surface_path: str, generated_dir: Path) -> Path:
    surface_path = PurePosixPath(relative_surface_path)
    if surface_path.parts and surface_path.parts[0] == "generated":
        return generated_dir.resolve().joinpath(*surface_path.parts[1:])
    return REPO_ROOT.joinpath(*surface_path.parts)


def validate_federation_entrypoints(
    federation_payload: dict[str, Any],
    generated_dir: Path,
    techniques_root: Path,
    agents_root: Path,
    playbooks_root: Path,
    kag_root: Path,
    aoa_root: Path,
    tos_root: Path,
    issues: list[ValidationIssue],
) -> None:
    roots = {
        "aoa-routing": generated_dir.resolve(),
        "aoa-techniques": techniques_root.resolve(),
        AGENTS_REPO: agents_root.resolve(),
        PLAYBOOKS_REPO: playbooks_root.resolve(),
        KAG_REPO: kag_root.resolve(),
        AOA_ROOT_REPO: aoa_root.resolve(),
        TOS_REPO: tos_root.resolve(),
    }

    try:
        source_inputs = ensure_list(
            federation_payload.get("source_inputs"),
            "federation_entrypoints.min.json.source_inputs",
        )
        root_entries = ensure_list(
            federation_payload.get("root_entries"),
            "federation_entrypoints.min.json.root_entries",
        )
        active_entry_kinds = ensure_string_list(
            federation_payload.get("active_entry_kinds"),
            "federation_entrypoints.min.json.active_entry_kinds",
        )
        declared_entry_kinds = ensure_string_list(
            federation_payload.get("declared_entry_kinds"),
            "federation_entrypoints.min.json.declared_entry_kinds",
        )
        entrypoints = ensure_list(
            federation_payload.get("entrypoints"),
            "federation_entrypoints.min.json.entrypoints",
        )
    except RouterError as exc:
        issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))
        return

    if active_entry_kinds != list(FEDERATION_ACTIVE_ENTRY_KINDS):
        issues.append(
            ValidationIssue(
                "federation_entrypoints.min.json",
                "active_entry_kinds must match the published v1 active federation entry kinds",
            )
        )
    if declared_entry_kinds != list(FEDERATION_DECLARED_ENTRY_KINDS):
        issues.append(
            ValidationIssue(
                "federation_entrypoints.min.json",
                "declared_entry_kinds must match the published v1 declared federation entry kinds",
            )
        )

    payload_cache: dict[tuple[str, str], dict[str, Any]] = {}

    def validate_source_path(repo_name: str, relative_path: str, location: str) -> None:
        repo_root = roots.get(repo_name)
        if repo_root is None:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"{location} references unknown repo '{repo_name}'",
                )
            )
            return
        if repo_name == "aoa-routing":
            target_path = resolve_routing_surface_path(relative_path, generated_dir)
        else:
            target_path = repo_root / relative_path
        if not target_path.exists():
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"{location} target '{repo_name}/{relative_path}' is missing",
                )
            )

    def load_target_payload(repo_name: str, relative_path: str) -> dict[str, Any] | None:
        cache_key = (repo_name, relative_path)
        if cache_key in payload_cache:
            return payload_cache[cache_key]
        repo_root = roots.get(repo_name)
        if repo_root is None:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"unknown repo '{repo_name}' while loading {relative_path}",
                )
            )
            return None
        if repo_name == "aoa-routing":
            target_path = resolve_routing_surface_path(relative_path, generated_dir)
        else:
            target_path = repo_root / relative_path
        location = f"{repo_name}/{relative_path}"
        try:
            payload = ensure_mapping(load_json_file(target_path), location)
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            return None
        payload_cache[cache_key] = payload
        return payload

    def validate_repo_ref(raw_ref: Any, location: str, *, allow_route_generated: bool) -> None:
        try:
            repo_name, relative_path = ensure_repo_qualified_ref(raw_ref, location)
        except RouterError as exc:
            issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))
            return
        if not allow_route_generated and repo_name == "aoa-routing" and relative_path.startswith("generated/"):
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"{location} must not point authority at aoa-routing/generated/*",
                )
            )
        validate_source_path(repo_name, relative_path, location)

    def validate_action(raw_action: Any, location: str) -> None:
        try:
            action = ensure_mapping(raw_action, location)
            target_repo = action.get("target_repo")
            if not isinstance(target_repo, str) or target_repo not in roots:
                raise RouterError(f"{location}.target_repo must reference a known repo")
            target_surface = ensure_repo_relative_path(
                action.get("target_surface"),
                f"{location}.target_surface",
            )
            match_key = action.get("match_key")
            target_value = action.get("target_value")
            if not isinstance(match_key, str) or not match_key.strip():
                raise RouterError(f"{location}.match_key must be a non-empty string")
            if not isinstance(target_value, str) or not target_value.strip():
                raise RouterError(f"{location}.target_value must be a non-empty string")
        except RouterError as exc:
            issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))
            return

        if Path(target_surface).suffix.lower() == ".md":
            if match_key != "path":
                issues.append(
                    ValidationIssue(
                        "federation_entrypoints.min.json",
                        f"{location} must use match_key 'path' for markdown inspect targets",
                    )
                )
            if target_value != target_surface:
                issues.append(
                    ValidationIssue(
                        "federation_entrypoints.min.json",
                        f"{location}.target_value must stay '{target_surface}' for markdown inspect targets",
                    )
                )
            validate_source_path(target_repo, target_surface, location)
            return

        payload = load_target_payload(target_repo, target_surface)
        if payload is None:
            return
        try:
            entries = load_surface_entries_for_validation(payload, target_surface)
        except RouterError as exc:
            issues.append(ValidationIssue(f"{target_repo}/{target_surface}", str(exc)))
            return
        if not any(isinstance(entry, dict) and entry.get(match_key) == target_value for entry in entries):
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"{location} target '{target_value}' was not found in {target_repo}/{target_surface}",
                )
            )

    for index, raw_source_input in enumerate(source_inputs):
        location = f"federation_entrypoints.min.json.source_inputs[{index}]"
        try:
            source_input = ensure_mapping(raw_source_input, location)
            repo_name = ensure_string(source_input.get("repo"), f"{location}.repo")
            relative_path = ensure_repo_relative_path(source_input.get("ref"), f"{location}.ref")
        except RouterError as exc:
            issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))
            continue
        validate_source_path(repo_name, relative_path, location)

    try:
        load_tos_tiny_entry_route(tos_root)
    except RouterError as exc:
        issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))

    root_ids: set[str] = set()
    entry_ids_by_kind: dict[str, set[str]] = {kind: set() for kind in FEDERATION_ACTIVE_ENTRY_KINDS}
    all_entry_ids: set[str] = set()

    for index, raw_root_entry in enumerate(root_entries):
        location = f"federation_entrypoints.min.json.root_entries[{index}]"
        try:
            root_entry = ensure_mapping(raw_root_entry, location)
            root_id = ensure_string(root_entry.get("id"), f"{location}.id")
        except RouterError as exc:
            issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))
            continue
        root_ids.add(root_id)
        all_entry_ids.add(root_id)
        validate_repo_ref(root_entry.get("capsule_surface"), f"{location}.capsule_surface", allow_route_generated=True)
        validate_repo_ref(root_entry.get("authority_surface"), f"{location}.authority_surface", allow_route_generated=False)
        next_actions = root_entry.get("next_actions")
        if isinstance(next_actions, list):
            for action_index, action in enumerate(next_actions):
                validate_action(action, f"{location}.next_actions[{action_index}]")
        fallback = root_entry.get("fallback")
        validate_action(fallback, f"{location}.fallback")
        next_hops = root_entry.get("next_hops")
        if isinstance(next_hops, list):
            for hop_index, raw_hop in enumerate(next_hops):
                hop_location = f"{location}.next_hops[{hop_index}]"
                if not isinstance(raw_hop, dict):
                    issues.append(ValidationIssue("federation_entrypoints.min.json", f"{hop_location} must be an object"))
                    continue
                hop_kind = raw_hop.get("kind")
                hop_id = raw_hop.get("id")
                if hop_kind not in FEDERATION_ACTIVE_ENTRY_KINDS or not isinstance(hop_id, str):
                    issues.append(
                        ValidationIssue(
                            "federation_entrypoints.min.json",
                            f"{hop_location} must reference an active federation entry kind and id",
                        )
                    )

    if root_ids != set(FEDERATION_ROOT_IDS):
        issues.append(
            ValidationIssue(
                "federation_entrypoints.min.json",
                "root_entries must publish exactly aoa-root and tos-root in v1",
            )
        )

    tos_root_entry = next(
        (
            raw_root_entry
            for raw_root_entry in root_entries
            if isinstance(raw_root_entry, dict) and raw_root_entry.get("id") == "tos-root"
        ),
        None,
    )
    if isinstance(tos_root_entry, dict):
        next_actions = tos_root_entry.get("next_actions")
        if not isinstance(next_actions, list) or not next_actions:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    "tos-root must publish the current ToS tiny-entry handoff as its first next_action",
                )
            )
        else:
            expected_actions = [
                {
                    "verb": "inspect",
                    "target_repo": TOS_REPO,
                    "target_surface": TOS_TINY_ENTRY_ROUTE_PATH,
                    "match_key": "route_id",
                    "target_value": TOS_TINY_ENTRY_ROUTE_ID,
                },
                {
                    "verb": "inspect",
                    "target_repo": PAIRING_SURFACE_REPO,
                    "target_surface": FEDERATION_ENTRYPOINTS_FILE,
                    "match_key": "id",
                    "target_value": TOS_KAG_VIEW_ENTRY_ID,
                },
                {
                    "verb": "inspect",
                    "target_repo": PAIRING_SURFACE_REPO,
                    "target_surface": FEDERATION_ENTRYPOINTS_FILE,
                    "match_key": "id",
                    "target_value": "AOA-P-0009",
                },
            ]
            if any(
                isinstance(action, dict)
                and action.get("target_repo") == KAG_REPO
                and action.get("target_surface") == TOS_ROUTE_RETRIEVAL_SURFACE_REF
                for action in next_actions
            ):
                issues.append(
                    ValidationIssue(
                        "federation_entrypoints.min.json",
                        "tos-root must stay tree-first and must not point directly to the aoa-kag Zarathustra retrieval adjunct",
                    )
                )
            if len(next_actions) != len(expected_actions):
                issues.append(
                    ValidationIssue(
                        "federation_entrypoints.min.json",
                        "tos-root must publish exactly three bounded next_actions in the current routing wave",
                    )
                )
            for action_index, expected_action in enumerate(expected_actions):
                if action_index >= len(next_actions):
                    break
                action = next_actions[action_index]
                if not isinstance(action, dict):
                    issues.append(
                        ValidationIssue(
                            "federation_entrypoints.min.json",
                            f"tos-root next_actions[{action_index}] must be an action object",
                        )
                    )
                    continue
                for key, expected_value in expected_action.items():
                    if action.get(key) != expected_value:
                        issues.append(
                            ValidationIssue(
                                "federation_entrypoints.min.json",
                                f"tos-root next_actions[{action_index}].{key} must stay '{expected_value}'",
                            )
                        )
        if tos_root_entry.get("next_hops") != [
            {"kind": "kag_view", "id": TOS_KAG_VIEW_ENTRY_ID},
            {"kind": "playbook", "id": TOS_KAG_VIEW_PLAYBOOK_ENTRY_ID},
        ]:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    "tos-root next_hops must stay bounded to the ToS-specific KAG view and AOA-P-0009 in the current routing wave",
                )
            )

    for index, raw_entry in enumerate(entrypoints):
        location = f"federation_entrypoints.min.json.entrypoints[{index}]"
        try:
            entry = ensure_mapping(raw_entry, location)
            entry_kind = entry.get("kind")
            entry_id = ensure_string(entry.get("id"), f"{location}.id")
        except RouterError as exc:
            issues.append(ValidationIssue("federation_entrypoints.min.json", str(exc)))
            continue
        if entry_kind not in FEDERATION_ACTIVE_ENTRY_KINDS:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"{location}.kind must be one of the active federation entry kinds",
                )
            )
            continue
        if entry_kind in declared_entry_kinds:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"{location}.kind must not use a declared-but-inactive entry kind",
                )
            )
        entry_ids_by_kind.setdefault(entry_kind, set()).add(entry_id)
        if entry_id in all_entry_ids:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"{location}.id duplicates another federation root or entry id",
                )
            )
        all_entry_ids.add(entry_id)
        validate_repo_ref(entry.get("capsule_surface"), f"{location}.capsule_surface", allow_route_generated=True)
        validate_repo_ref(entry.get("authority_surface"), f"{location}.authority_surface", allow_route_generated=False)
        next_actions = entry.get("next_actions")
        if isinstance(next_actions, list):
            for action_index, action in enumerate(next_actions):
                validate_action(action, f"{location}.next_actions[{action_index}]")
        validate_action(entry.get("fallback"), f"{location}.fallback")
        risk = entry.get("risk")
        if not isinstance(risk, str) or not risk.strip():
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    f"{location}.risk must be a non-empty string",
                )
            )
        next_hops = entry.get("next_hops")
        if isinstance(next_hops, list):
            for hop_index, raw_hop in enumerate(next_hops):
                hop_location = f"{location}.next_hops[{hop_index}]"
                if not isinstance(raw_hop, dict):
                    issues.append(ValidationIssue("federation_entrypoints.min.json", f"{hop_location} must be an object"))
                    continue
                hop_kind = raw_hop.get("kind")
                hop_id = raw_hop.get("id")
                if hop_kind not in FEDERATION_ACTIVE_ENTRY_KINDS or not isinstance(hop_id, str):
                    issues.append(
                        ValidationIssue(
                            "federation_entrypoints.min.json",
                            f"{hop_location} must reference an active federation entry kind and id",
                        )
                    )

    for index, raw_root_entry in enumerate(root_entries):
        location = f"federation_entrypoints.min.json.root_entries[{index}]"
        if not isinstance(raw_root_entry, dict):
            continue
        next_hops = raw_root_entry.get("next_hops")
        if not isinstance(next_hops, list):
            continue
        for hop_index, raw_hop in enumerate(next_hops):
            if not isinstance(raw_hop, dict):
                continue
            hop_kind = raw_hop.get("kind")
            hop_id = raw_hop.get("id")
            if isinstance(hop_kind, str) and isinstance(hop_id, str) and hop_id not in entry_ids_by_kind.get(hop_kind, set()):
                issues.append(
                    ValidationIssue(
                        "federation_entrypoints.min.json",
                        f"{location}.next_hops[{hop_index}] must point to a live federation entry",
                    )
                )

    for index, raw_entry in enumerate(entrypoints):
        location = f"federation_entrypoints.min.json.entrypoints[{index}]"
        if not isinstance(raw_entry, dict):
            continue
        next_hops = raw_entry.get("next_hops")
        if not isinstance(next_hops, list):
            continue
        for hop_index, raw_hop in enumerate(next_hops):
            if not isinstance(raw_hop, dict):
                continue
            hop_kind = raw_hop.get("kind")
            hop_id = raw_hop.get("id")
            if isinstance(hop_kind, str) and isinstance(hop_id, str) and hop_id not in entry_ids_by_kind.get(hop_kind, set()):
                issues.append(
                    ValidationIssue(
                        "federation_entrypoints.min.json",
                        f"{location}.next_hops[{hop_index}] must point to a live federation entry",
                    )
                )

    if entry_ids_by_kind.get("kag_view", set()) != EXPECTED_KAG_VIEW_IDS:
        issues.append(
            ValidationIssue(
                "federation_entrypoints.min.json",
                "kag_view entries must publish exactly aoa-techniques and Tree-of-Sophia in the current routing wave",
            )
        )

    entry_by_kind_and_id = {
        (entry.get("kind"), entry.get("id")): entry
        for entry in entrypoints
        if isinstance(entry, dict)
    }

    aoa_techniques_kag_view = entry_by_kind_and_id.get(
        ("kag_view", FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID)
    )
    if isinstance(aoa_techniques_kag_view, dict):
        if aoa_techniques_kag_view.get("next_actions") != [
            {
                "verb": "inspect",
                "target_repo": "aoa-techniques",
                "target_surface": "generated/repo_doc_surface_manifest.min.json",
                "match_key": "doc_id",
                "target_value": "readme",
            },
            {
                "verb": "inspect",
                "target_repo": "aoa-techniques",
                "target_surface": "generated/technique_catalog.min.json",
                "match_key": "id",
                "target_value": AOA_TECHNIQUES_KAG_VIEW_EXAMPLE_OBJECT_IDS[0],
            },
        ]:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    "aoa-techniques kag_view must keep the current repo-doc and technique-catalog handoff actions",
                )
            )
        if aoa_techniques_kag_view.get("next_hops") != [
            {"kind": "tier", "id": FEDERATION_DEFAULT_TIER_ENTRY_ID},
            {"kind": "playbook", "id": FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID},
        ]:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    "aoa-techniques kag_view must keep router and AOA-P-0008 as its bounded next hops",
                )
            )

    tos_kag_view = entry_by_kind_and_id.get(("kag_view", TOS_KAG_VIEW_ENTRY_ID))
    if isinstance(tos_kag_view, dict):
        if tos_kag_view.get("next_actions") != [
            {
                "verb": "inspect",
                "target_repo": TOS_REPO,
                "target_surface": TOS_TINY_ENTRY_DOCTRINE_PATH,
                "match_key": "path",
                "target_value": TOS_TINY_ENTRY_DOCTRINE_PATH,
            },
            {
                "verb": "inspect",
                "target_repo": TOS_REPO,
                "target_surface": TOS_TINY_ENTRY_ROUTE_PATH,
                "match_key": "route_id",
                "target_value": TOS_TINY_ENTRY_ROUTE_ID,
            },
            {
                "verb": "inspect",
                "target_repo": KAG_REPO,
                "target_surface": TOS_ROUTE_RETRIEVAL_SURFACE_REF,
                "match_key": "retrieval_id",
                "target_value": TOS_ROUTE_RETRIEVAL_ID,
            },
        ]:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    "Tree-of-Sophia kag_view must point first to TINY_ENTRY_ROUTE doctrine, then to the current tiny-entry route example, and finally to the bounded AOA-K-0011 retrieval adjunct",
                )
            )
        if tos_kag_view.get("next_hops") != [
            {"kind": "tier", "id": FEDERATION_DEFAULT_TIER_ENTRY_ID},
            {"kind": "playbook", "id": TOS_KAG_VIEW_PLAYBOOK_ENTRY_ID},
        ]:
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    "Tree-of-Sophia kag_view must keep router and AOA-P-0009 as its bounded next hops",
                )
            )
        risk = tos_kag_view.get("risk")
        if (
            not isinstance(risk, str)
            or "Tree-of-Sophia remains authoritative" not in risk
            or "AOA-K-0011 is only a bounded handles-only adjunct" not in risk
        ):
            issues.append(
                ValidationIssue(
                    "federation_entrypoints.min.json",
                    "Tree-of-Sophia kag_view risk text must explicitly preserve ToS authority in Tree-of-Sophia and bound AOA-K-0011 as a handles-only adjunct",
                )
            )


def validate_return_navigation_hints(
    return_payload: dict[str, Any],
    generated_dir: Path,
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
    agents_root: Path,
    aoa_root: Path,
    playbooks_root: Path,
    kag_root: Path,
    tos_root: Path,
    issues: list[ValidationIssue],
) -> None:
    location_prefix = Path(RETURN_NAVIGATION_HINTS_FILE).name
    roots = {
        "aoa-routing": generated_dir.resolve(),
        "aoa-techniques": techniques_root.resolve(),
        "aoa-skills": skills_root.resolve(),
        "aoa-evals": evals_root.resolve(),
        "aoa-memo": memo_root.resolve(),
        AGENTS_REPO: agents_root.resolve(),
        AOA_ROOT_REPO: aoa_root.resolve(),
        PLAYBOOKS_REPO: playbooks_root.resolve(),
        KAG_REPO: kag_root.resolve(),
        TOS_REPO: tos_root.resolve(),
    }
    expected_root_owner = {
        "aoa-root": AOA_ROOT_REPO,
        "tos-root": TOS_REPO,
    }
    expected_kind_owner = {
        "agent": AGENTS_REPO,
        "tier": AGENTS_REPO,
        "playbook": PLAYBOOKS_REPO,
        "kag_view": KAG_REPO,
    }
    payload_cache: dict[tuple[str, str], dict[str, Any]] = {}

    def resolve_repo_target(repo_name: str, relative_path: str) -> Path:
        if repo_name == "aoa-routing":
            return resolve_routing_surface_path(relative_path, generated_dir)
        return roots[repo_name] / relative_path

    def load_target_payload(repo_name: str, relative_path: str) -> dict[str, Any] | None:
        cache_key = (repo_name, relative_path)
        if cache_key in payload_cache:
            return payload_cache[cache_key]
        target_path = resolve_repo_target(repo_name, relative_path)
        location = f"{repo_name}/{relative_path}"
        try:
            payload = ensure_mapping(load_json_file(target_path), location)
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            return None
        payload_cache[cache_key] = payload
        return payload

    def validate_action(
        raw_action: Any,
        location: str,
        *,
        router_owned_allowed: bool,
    ) -> dict[str, str] | None:
        try:
            action = ensure_mapping(raw_action, location)
            normalized = {
                "verb": ensure_string(action.get("verb"), f"{location}.verb"),
                "target_repo": ensure_string(action.get("target_repo"), f"{location}.target_repo"),
                "target_surface": ensure_repo_relative_path(
                    action.get("target_surface"),
                    f"{location}.target_surface",
                ),
            }
            match_field = action.get("match_field")
            target_value = action.get("target_value")
            section_key_field = action.get("section_key_field")
            if match_field is not None:
                normalized["match_field"] = ensure_string(match_field, f"{location}.match_field")
            if target_value is not None:
                normalized["target_value"] = ensure_string(target_value, f"{location}.target_value")
            if section_key_field is not None:
                normalized["section_key_field"] = ensure_string(
                    section_key_field,
                    f"{location}.section_key_field",
                )
        except RouterError as exc:
            issues.append(ValidationIssue(location_prefix, str(exc)))
            return None

        target_repo = normalized["target_repo"]
        target_surface = normalized["target_surface"]
        if target_repo not in roots:
            issues.append(
                ValidationIssue(location_prefix, f"{location}.target_repo must reference a known repo")
            )
            return None
        if target_repo == "aoa-routing" and not router_owned_allowed:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location} must not point primary authority or thin-router re-entry at aoa-routing",
                )
            )
        target_path = resolve_repo_target(target_repo, target_surface)
        if not target_path.exists():
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location} target '{target_repo}/{target_surface}' is missing",
                )
            )
            return normalized

        is_markdown = Path(target_surface).suffix.lower() == ".md"
        if is_markdown:
            if any(key in normalized for key in ("match_field", "target_value", "section_key_field")):
                issues.append(
                    ValidationIssue(
                        location_prefix,
                        f"{location} markdown targets must not define match or section fields",
                    )
                )
            return normalized

        if "target_value" in normalized and "match_field" not in normalized:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.target_value requires match_field",
                )
            )
            return normalized
        if "section_key_field" in normalized and "match_field" not in normalized:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.section_key_field requires match_field",
                )
            )
            return normalized
        if "match_field" not in normalized and "section_key_field" not in normalized:
            return normalized

        payload = load_target_payload(target_repo, target_surface)
        if payload is None:
            return normalized
        try:
            entries = load_surface_entries_for_validation(payload, target_surface)
        except RouterError as exc:
            issues.append(ValidationIssue(f"{target_repo}/{target_surface}", str(exc)))
            return normalized

        match_field = normalized.get("match_field")
        target_value = normalized.get("target_value")
        section_key_field = normalized.get("section_key_field")
        matched_any = False
        found_target = False
        for index, raw_entry in enumerate(entries):
            entry_location = f"{target_repo}/{target_surface}[{index}]"
            try:
                entry = ensure_mapping(raw_entry, entry_location)
            except RouterError as exc:
                issues.append(ValidationIssue(f"{target_repo}/{target_surface}", str(exc)))
                continue
            if match_field is None:
                continue
            raw_match = entry.get(match_field)
            if not isinstance(raw_match, str) or not raw_match.strip():
                continue
            matched_any = True
            if target_value is not None and raw_match == target_value:
                found_target = True
            if section_key_field is None:
                continue
            try:
                sections = ensure_list(entry.get("sections"), f"{entry_location}.sections")
            except RouterError as exc:
                issues.append(ValidationIssue(f"{target_repo}/{target_surface}", str(exc)))
                continue
            for section_index, raw_section in enumerate(sections):
                section_location = f"{entry_location}.sections[{section_index}]"
                try:
                    section = ensure_mapping(raw_section, section_location)
                    ensure_string(section.get(section_key_field), f"{section_location}.{section_key_field}")
                except RouterError as exc:
                    issues.append(ValidationIssue(f"{target_repo}/{target_surface}", str(exc)))
        if match_field is not None and not matched_any:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location} target '{target_repo}/{target_surface}' does not expose match_field '{match_field}'",
                )
            )
        if target_value is not None and not found_target:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location} target '{target_value}' was not found in {target_repo}/{target_surface}",
                )
            )
        return normalized

    try:
        thin_router_returns = ensure_list(
            return_payload.get("thin_router_returns"),
            f"{location_prefix}.thin_router_returns",
        )
        federation_root_returns = ensure_list(
            return_payload.get("federation_root_returns"),
            f"{location_prefix}.federation_root_returns",
        )
        federation_kind_returns = ensure_list(
            return_payload.get("federation_kind_returns"),
            f"{location_prefix}.federation_kind_returns",
        )
    except RouterError as exc:
        issues.append(ValidationIssue(location_prefix, str(exc)))
        return

    seen_thin_kinds: set[str] = set()
    for index, raw_record in enumerate(thin_router_returns):
        location = f"{location_prefix}.thin_router_returns[{index}]"
        try:
            record = ensure_mapping(raw_record, location)
            context_kind = ensure_string(record.get("context_kind"), f"{location}.context_kind")
            source_repo = ensure_string(record.get("source_repo"), f"{location}.source_repo")
        except RouterError as exc:
            issues.append(ValidationIssue(location_prefix, str(exc)))
            continue
        seen_thin_kinds.add(context_kind)
        expected_repo = CANONICAL_REPO_BY_KIND.get(context_kind)
        if expected_repo is not None and source_repo != expected_repo:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.source_repo must stay '{expected_repo}' for kind '{context_kind}'",
                )
            )
        primary_action = validate_action(
            record.get("primary_action"),
            f"{location}.primary_action",
            router_owned_allowed=False,
        )
        secondary_action = None
        if record.get("secondary_action") is not None:
            secondary_action = validate_action(
                record.get("secondary_action"),
                f"{location}.secondary_action",
                router_owned_allowed=False,
            )
        if primary_action is not None and primary_action["target_repo"] != source_repo:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.primary_action.target_repo must equal source_repo '{source_repo}'",
                )
            )
        if secondary_action is not None and secondary_action["target_repo"] != source_repo:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.secondary_action.target_repo must equal source_repo '{source_repo}'",
                )
            )
        if context_kind == "memo":
            if primary_action is not None and (
                primary_action["target_repo"] != "aoa-memo"
                or primary_action["target_surface"] != MEMO_OBJECT_RETURN_READY_CONTRACT
            ):
                issues.append(
                    ValidationIssue(
                        location_prefix,
                        "memo return primary_action must point to aoa-memo/examples/recall_contract.object.working.return.json",
                    )
                )
            if secondary_action is not None and (
                secondary_action["target_repo"] != "aoa-memo"
                or secondary_action["target_surface"] != MEMO_OBJECT_INSPECT_SURFACE_FILE
            ):
                issues.append(
                    ValidationIssue(
                        location_prefix,
                        "memo return secondary_action must point to aoa-memo/generated/memory_object_catalog.min.json",
                    )
                )
    missing_thin_kinds = sorted(set(ACTIVE_KINDS) - seen_thin_kinds)
    for missing_kind in missing_thin_kinds:
        issues.append(
            ValidationIssue(
                location_prefix,
                f"{location_prefix}.thin_router_returns must include context_kind '{missing_kind}'",
            )
        )

    seen_root_ids: set[str] = set()
    for index, raw_record in enumerate(federation_root_returns):
        location = f"{location_prefix}.federation_root_returns[{index}]"
        try:
            record = ensure_mapping(raw_record, location)
            root_id = ensure_string(record.get("root_id"), f"{location}.root_id")
            owner_repo = ensure_string(record.get("owner_repo"), f"{location}.owner_repo")
        except RouterError as exc:
            issues.append(ValidationIssue(location_prefix, str(exc)))
            continue
        seen_root_ids.add(root_id)
        expected_owner = expected_root_owner.get(root_id)
        if expected_owner is not None and owner_repo != expected_owner:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.owner_repo must stay '{expected_owner}' for root '{root_id}'",
                )
            )
        primary_action = validate_action(
            record.get("primary_action"),
            f"{location}.primary_action",
            router_owned_allowed=False,
        )
        fallback_action = validate_action(
            record.get("fallback_action"),
            f"{location}.fallback_action",
            router_owned_allowed=True,
        )
        if primary_action is not None and primary_action["target_repo"] != owner_repo:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.primary_action.target_repo must equal owner_repo '{owner_repo}'",
                )
            )
        if fallback_action is not None and fallback_action["target_repo"] != "aoa-routing":
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.fallback_action.target_repo must stay 'aoa-routing'",
                )
            )
    missing_root_ids = sorted(set(FEDERATION_ROOT_IDS) - seen_root_ids)
    for missing_root in missing_root_ids:
        issues.append(
            ValidationIssue(
                location_prefix,
                f"{location_prefix}.federation_root_returns must include root_id '{missing_root}'",
            )
        )

    seen_entry_kinds: set[str] = set()
    for index, raw_record in enumerate(federation_kind_returns):
        location = f"{location_prefix}.federation_kind_returns[{index}]"
        try:
            record = ensure_mapping(raw_record, location)
            entry_kind = ensure_string(record.get("entry_kind"), f"{location}.entry_kind")
            owner_repo = ensure_string(record.get("owner_repo"), f"{location}.owner_repo")
        except RouterError as exc:
            issues.append(ValidationIssue(location_prefix, str(exc)))
            continue
        seen_entry_kinds.add(entry_kind)
        expected_owner = expected_kind_owner.get(entry_kind)
        if expected_owner is not None and owner_repo != expected_owner:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.owner_repo must stay '{expected_owner}' for kind '{entry_kind}'",
                )
            )
        primary_action = validate_action(
            record.get("primary_action"),
            f"{location}.primary_action",
            router_owned_allowed=False,
        )
        fallback_action = validate_action(
            record.get("fallback_action"),
            f"{location}.fallback_action",
            router_owned_allowed=True,
        )
        if primary_action is not None and primary_action["target_repo"] != owner_repo:
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.primary_action.target_repo must equal owner_repo '{owner_repo}'",
                )
            )
        if fallback_action is not None and fallback_action["target_repo"] != "aoa-routing":
            issues.append(
                ValidationIssue(
                    location_prefix,
                    f"{location}.fallback_action.target_repo must stay 'aoa-routing'",
                )
            )
    missing_entry_kinds = sorted(set(FEDERATION_ACTIVE_ENTRY_KINDS) - seen_entry_kinds)
    for missing_kind in missing_entry_kinds:
        issues.append(
            ValidationIssue(
                location_prefix,
                f"{location_prefix}.federation_kind_returns must include entry_kind '{missing_kind}'",
            )
        )


def validate_pair_targets(
    registry_entries: list[dict[str, Any]],
    hints_payload: dict[str, Any],
    generated_dir: Path,
    issues: list[ValidationIssue],
) -> None:
    try:
        hints = ensure_list(hints_payload.get("hints"), "task_to_surface_hints.json.hints")
    except RouterError as exc:
        issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
        return

    registry_index = {
        (entry["kind"], entry["id"]): entry
        for entry in registry_entries
        if isinstance(entry.get("kind"), str) and isinstance(entry.get("id"), str)
    }
    expected_matches_by_kind = {
        kind: {
            entry["id"]
            for entry in registry_entries
            if entry.get("kind") == kind and isinstance(entry.get("id"), str)
        }
        for kind in PAIRABLE_KINDS
    }

    loaded_payloads: dict[str, dict[str, Any]] = {}
    pair_entries_by_kind: dict[str, set[str]] = {kind: set() for kind in PAIRABLE_KINDS}
    validated_surface_files: set[str] = set()

    for index, raw_hint in enumerate(hints):
        try:
            hint = ensure_mapping(raw_hint, f"task_to_surface_hints.json.hints[{index}]")
        except RouterError as exc:
            issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
            continue
        kind = hint.get("kind")
        if kind not in PAIRABLE_KINDS or hint.get("enabled") is not True:
            continue
        actions = hint.get("actions")
        if not isinstance(actions, dict):
            continue
        pair = actions.get("pair")
        if not isinstance(pair, dict) or pair.get("enabled") is not True:
            continue

        surface_repo = pair.get("surface_repo")
        surface_file = pair.get("surface_file")
        match_field = pair.get("match_field")
        if surface_repo != PAIRING_SURFACE_REPO:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"pair action for kind '{kind}' must use surface_repo '{PAIRING_SURFACE_REPO}'",
                )
            )
            continue
        if not isinstance(surface_file, str) or not surface_file.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled pair action for kind '{kind}' must define surface_file",
                )
            )
            continue
        if not isinstance(match_field, str) or not match_field.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled pair action for kind '{kind}' must define match_field",
                )
            )
            continue

        try:
            relative_surface_file = ensure_repo_relative_path(
                surface_file,
                f"task_to_surface_hints.json.hints[{index}].actions.pair.surface_file",
            )
        except RouterError as exc:
            issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
            continue

        if relative_surface_file not in loaded_payloads:
            surface_path = resolve_routing_surface_path(relative_surface_file, generated_dir)
            location = f"aoa-routing/{relative_surface_file}"
            try:
                loaded_payloads[relative_surface_file] = ensure_mapping(load_json_file(surface_path), location)
            except RouterError as exc:
                issues.append(ValidationIssue(location, str(exc)))
                continue

        payload = loaded_payloads[relative_surface_file]
        try:
            pair_entries = load_surface_entries_for_validation(payload, relative_surface_file)
        except RouterError as exc:
            issues.append(ValidationIssue(f"aoa-routing/{relative_surface_file}", str(exc)))
            continue

        if relative_surface_file in validated_surface_files:
            continue
        validated_surface_files.add(relative_surface_file)

        for pair_index, raw_entry in enumerate(pair_entries):
            location = f"aoa-routing/{relative_surface_file}.entries[{pair_index}]"
            try:
                entry = ensure_mapping(raw_entry, location)
            except RouterError as exc:
                issues.append(ValidationIssue(f"aoa-routing/{relative_surface_file}", str(exc)))
                continue
            entry_kind = entry.get("kind")
            entry_id = entry.get("id")
            if entry_kind not in PAIRABLE_KINDS or not isinstance(entry_id, str):
                continue
            pair_entries_by_kind[entry_kind].add(entry_id)
            pairs = entry.get("pairs")
            if not isinstance(pairs, list):
                issues.append(ValidationIssue(location, "pairs must be a list"))
                continue
            seen_targets: set[tuple[str, str, str]] = set()
            for target_index, raw_pair in enumerate(pairs):
                pair_location = f"{location}.pairs[{target_index}]"
                if not isinstance(raw_pair, dict):
                    issues.append(ValidationIssue(pair_location, "pair target must be an object"))
                    continue
                target_kind = raw_pair.get("kind")
                target_id = raw_pair.get("id")
                relation = raw_pair.get("relation")
                if target_kind == "memo":
                    issues.append(ValidationIssue(pair_location, "memo pair hops are not allowed"))
                    continue
                if target_kind not in PAIRABLE_KINDS:
                    issues.append(
                        ValidationIssue(
                            pair_location,
                            "pair target kind must be technique, skill, or eval",
                        )
                    )
                    continue
                if not isinstance(target_id, str):
                    continue
                if (target_kind, target_id) not in registry_index:
                    issues.append(
                        ValidationIssue(
                            pair_location,
                            f"pair target {target_kind}:{target_id} must exist in the registry",
                        )
                    )
                if not isinstance(relation, str):
                    continue
                if target_kind == entry_kind:
                    if entry_kind != "technique":
                        issues.append(
                            ValidationIssue(
                                pair_location,
                                "same-kind pairing is only allowed for techniques",
                            )
                        )
                    elif entry_id not in KAG_SOURCE_LIFT_TECHNIQUE_SET or target_id not in KAG_SOURCE_LIFT_TECHNIQUE_SET:
                        issues.append(
                            ValidationIssue(
                                pair_location,
                                "same-kind pairing must stay within the KAG/source-lift family",
                            )
                        )
                    elif relation not in DIRECT_RELATION_TYPES_SET:
                        issues.append(
                            ValidationIssue(
                                pair_location,
                                "same-kind pairing must use a supported direct relation type",
                            )
                        )
                elif relation not in {"requires", "required_by"}:
                    issues.append(
                        ValidationIssue(
                            pair_location,
                            "cross-kind pairing must use relation 'requires' or 'required_by'",
                        )
                    )
                target_key = (target_kind, target_id, relation)
                if target_key in seen_targets:
                    issues.append(ValidationIssue(pair_location, "duplicate pair target"))
                seen_targets.add(target_key)

    for kind, expected_matches in expected_matches_by_kind.items():
        missing_matches = sorted(expected_matches - pair_entries_by_kind[kind])
        for match_value in missing_matches:
            issues.append(
                ValidationIssue(
                    "pairing_hints.min.json",
                    f"pair surface is missing {kind} match '{match_value}'",
                )
            )


def validate_tiny_model_entrypoints(
    tiny_payload: dict[str, Any],
    generated_dir: Path,
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
    agents_root: Path,
    playbooks_root: Path,
    kag_root: Path,
    aoa_root: Path,
    tos_root: Path,
    issues: list[ValidationIssue],
) -> None:
    roots = {
        "aoa-routing": generated_dir.resolve(),
        "aoa-techniques": techniques_root.resolve(),
        "aoa-skills": skills_root.resolve(),
        "aoa-evals": evals_root.resolve(),
        "aoa-memo": memo_root.resolve(),
        AGENTS_REPO: agents_root.resolve(),
        PLAYBOOKS_REPO: playbooks_root.resolve(),
        KAG_REPO: kag_root.resolve(),
        AOA_ROOT_REPO: aoa_root.resolve(),
        TOS_REPO: tos_root.resolve(),
    }

    try:
        queries = ensure_list(tiny_payload.get("queries"), "tiny_model_entrypoints.json.queries")
        starters = ensure_list(tiny_payload.get("starters"), "tiny_model_entrypoints.json.starters")
        federation_queries = ensure_list(
            tiny_payload.get("federation_queries"),
            "tiny_model_entrypoints.json.federation_queries",
        )
        federation_starters = ensure_list(
            tiny_payload.get("federation_starters"),
            "tiny_model_entrypoints.json.federation_starters",
        )
    except RouterError as exc:
        issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
        return

    starter_names: set[str] = set()

    def load_target_payload(source_repo: str, surface_file: str) -> dict[str, Any] | None:
        surface_root = roots.get(source_repo)
        if surface_root is None:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"unknown source_repo '{source_repo}' in tiny-model entrypoints",
                )
            )
            return None
        try:
            relative_surface_file = ensure_repo_relative_path(
                surface_file,
                f"tiny_model_entrypoints.json.{source_repo}.target_surface",
            )
        except RouterError as exc:
            issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
            return None
        if source_repo == "aoa-routing":
            surface_path = resolve_routing_surface_path(relative_surface_file, generated_dir)
        else:
            surface_path = surface_root / relative_surface_file
        location = f"{source_repo}/{relative_surface_file}"
        try:
            return ensure_mapping(load_json_file(surface_path), location)
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            return None

    def find_surface_entry(
        entries: list[dict[str, Any]],
        *,
        match_key: str,
        target_value: str,
    ) -> dict[str, Any] | None:
        for raw_entry in entries:
            if not isinstance(raw_entry, dict):
                continue
            if raw_entry.get(match_key) == target_value:
                return raw_entry
        return None

    def validate_recall_target(
        *,
        consumer_label: str,
        location: str,
        matched_entry: dict[str, Any],
        recall_family: Any,
        recall_mode: Any,
        require_mode: bool,
    ) -> None:
        actions = matched_entry.get("actions") if isinstance(matched_entry, dict) else None
        recall = actions.get("recall") if isinstance(actions, dict) else None
        if not isinstance(recall, dict) or recall.get("enabled") is not True:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} points to a target without enabled recall routing",
                )
            )
            return

        selected_recall = recall
        selected_family: str | None = None
        if recall_family is not None:
            if not isinstance(recall_family, str) or not recall_family.strip():
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"{consumer_label} must define a non-empty recall_family when present",
                    )
                )
                return
            parallel_families = recall.get("parallel_families")
            if not isinstance(parallel_families, dict):
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"{consumer_label} must target a published recall family '{recall_family}'",
                    )
                )
                return
            family_payload = parallel_families.get(recall_family)
            if not isinstance(family_payload, dict):
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"{consumer_label} must target a published recall family '{recall_family}'",
                    )
                )
                return
            selected_recall = family_payload
            selected_family = recall_family

        if require_mode and (not isinstance(recall_mode, str) or not recall_mode.strip()):
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} must define recall_mode",
                )
            )
            return
        if recall_mode is None:
            return
        if not isinstance(recall_mode, str) or not recall_mode.strip():
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} must define a non-empty recall_mode when present",
                )
            )
            return
        try:
            supported_modes = ensure_string_list(
                selected_recall.get("supported_modes"),
                f"{location}.recall_mode",
            )
        except RouterError as exc:
            issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
            return
        if recall_mode not in supported_modes:
            family_message = ""
            if selected_family is not None:
                family_message = f" for recall family '{selected_family}'"
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} uses unsupported recall mode '{recall_mode}'{family_message}",
                )
            )
        contracts_by_mode = selected_recall.get("contracts_by_mode")
        if not isinstance(contracts_by_mode, dict) or recall_mode not in contracts_by_mode:
            family_message = ""
            if selected_family is not None:
                family_message = f" in recall family '{selected_family}'"
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} must target a published recall contract for mode '{recall_mode}'{family_message}",
                )
            )

    for index, raw_query in enumerate(queries):
        location = f"tiny_model_entrypoints.json.queries[{index}]"
        try:
            query = ensure_mapping(raw_query, location)
            source_repo = query.get("source_repo")
            surface_file = query.get("target_surface")
            if not isinstance(source_repo, str) or not isinstance(surface_file, str):
                continue
            payload = load_target_payload(source_repo, surface_file)
            if payload is None:
                continue
            verb = query.get("verb")
            recall_mode = query.get("recall_mode")
            recall_family = query.get("recall_family")
            if verb != "recall":
                if recall_mode is not None:
                    issues.append(
                        ValidationIssue(
                            "tiny_model_entrypoints.json",
                            f"non-recall query '{location}' must not define recall_mode",
                        )
                    )
                if recall_family is not None:
                    issues.append(
                        ValidationIssue(
                            "tiny_model_entrypoints.json",
                            f"non-recall query '{location}' must not define recall_family",
                        )
                    )
                continue
            allowed_kinds = query.get("allowed_kinds")
            if not isinstance(allowed_kinds, list) or len(allowed_kinds) != 1:
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"recall query '{location}' must target exactly one allowed kind",
                    )
                )
                continue
            target_value = allowed_kinds[0]
            match_key = query.get("match_key")
            if not isinstance(match_key, str) or match_key != "kind":
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"recall query '{location}' must use match_key 'kind'",
                    )
                )
                continue
            if not isinstance(target_value, str) or not target_value.strip():
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"recall query '{location}' must target a non-empty kind value",
                    )
                )
                continue
            entries = load_surface_entries_for_validation(payload, surface_file)
            matched_entry = find_surface_entry(entries, match_key=match_key, target_value=target_value)
            if matched_entry is None:
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"recall query '{location}' target '{target_value}' was not found in {source_repo}/{surface_file}",
                    )
                )
                continue
            validate_recall_target(
                consumer_label=f"recall query '{location}'",
                location=location,
                matched_entry=matched_entry,
                recall_family=recall_family,
                recall_mode=recall_mode,
                require_mode=False,
            )
        except RouterError as exc:
            issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))

    for index, raw_starter in enumerate(starters):
        location = f"tiny_model_entrypoints.json.starters[{index}]"
        try:
            starter = ensure_mapping(raw_starter, location)
        except RouterError as exc:
            issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
            continue
        starter_name = starter.get("name")
        if isinstance(starter_name, str):
            if starter_name in starter_names:
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"starter names must be unique; found duplicate '{starter_name}'",
                    )
                )
            else:
                starter_names.add(starter_name)
        source_repo = starter.get("source_repo")
        surface_file = starter.get("target_surface")
        verb = starter.get("verb")
        match_key = starter.get("match_key")
        target_value = starter.get("target_value")
        recall_family = starter.get("recall_family")
        recall_mode = starter.get("recall_mode")
        if not isinstance(source_repo, str) or not isinstance(surface_file, str):
            continue
        payload = load_target_payload(source_repo, surface_file)
        if payload is None:
            continue
        if not isinstance(match_key, str) or not isinstance(target_value, str):
            continue
        try:
            entries = load_surface_entries_for_validation(payload, surface_file)
        except RouterError as exc:
            issues.append(ValidationIssue(f"{source_repo}/{surface_file}", str(exc)))
            continue
        matched_entry = find_surface_entry(entries, match_key=match_key, target_value=target_value)
        if matched_entry is None:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"starter '{starter.get('name', index)}' target '{target_value}' was not found in {source_repo}/{surface_file}",
                )
            )
            continue
        if verb == "recall":
            validate_recall_target(
                consumer_label=f"recall starter '{starter.get('name', index)}'",
                location=location,
                matched_entry=matched_entry,
                recall_family=recall_family,
                recall_mode=recall_mode,
                require_mode=True,
            )
        elif recall_mode is not None:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"non-recall starter '{starter.get('name', index)}' must not define recall_mode",
                )
            )
        elif recall_family is not None:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"non-recall starter '{starter.get('name', index)}' must not define recall_family",
                )
            )

    def validate_federation_target(
        *,
        consumer_label: str,
        location: str,
        source_repo: str,
        surface_file: str,
        match_key: Any,
        target_value: Any,
        entry_kind: Any = None,
    ) -> None:
        payload = load_target_payload(source_repo, surface_file)
        if payload is None:
            return
        try:
            entries = load_surface_entries_for_validation(payload, surface_file)
        except RouterError as exc:
            issues.append(ValidationIssue(f"{source_repo}/{surface_file}", str(exc)))
            return
        if not isinstance(match_key, str) or not match_key.strip():
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} must define a non-empty match_key",
                )
            )
            return
        if not isinstance(target_value, str) or not target_value.strip():
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} must define a non-empty target_value",
                )
            )
            return
        matched_entry = find_surface_entry(entries, match_key=match_key, target_value=target_value)
        if matched_entry is None:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} target '{target_value}' was not found in {source_repo}/{surface_file}",
                )
            )
            return
        if entry_kind is not None and matched_entry.get("kind") != entry_kind:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"{consumer_label} must resolve to federation entry kind '{entry_kind}'",
                )
            )

    for index, raw_query in enumerate(federation_queries):
        location = f"tiny_model_entrypoints.json.federation_queries[{index}]"
        try:
            query = ensure_mapping(raw_query, location)
            name = ensure_string(query.get("name"), f"{location}.name")
            source_repo = ensure_string(query.get("source_repo"), f"{location}.source_repo")
            surface_file = ensure_repo_relative_path(
                query.get("target_surface"),
                f"{location}.target_surface",
            )
            if source_repo != "aoa-routing" or surface_file != FEDERATION_ENTRYPOINTS_FILE:
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"federation query '{name}' must target aoa-routing/{FEDERATION_ENTRYPOINTS_FILE}",
                    )
                )
            match_key = query.get("match_key")
        except RouterError as exc:
            issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
            continue

        if name == "federation-kind-pick":
            try:
                allowed_entry_kinds = ensure_string_list(
                    query.get("allowed_entry_kinds"),
                    f"{location}.allowed_entry_kinds",
                )
            except RouterError as exc:
                issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
                continue
            if allowed_entry_kinds != list(FEDERATION_ACTIVE_ENTRY_KINDS):
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        "federation-kind-pick must advertise the active federation entry kinds only",
                    )
                )
            if match_key != "kind":
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        "federation-kind-pick must use match_key 'kind'",
                    )
                )
        elif name == "federation-entry-inspect":
            try:
                allowed_entry_kinds = ensure_string_list(
                    query.get("allowed_entry_kinds"),
                    f"{location}.allowed_entry_kinds",
                )
            except RouterError as exc:
                issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
                continue
            if allowed_entry_kinds != list(FEDERATION_ACTIVE_ENTRY_KINDS):
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        "federation-entry-inspect must advertise the active federation entry kinds only",
                    )
                )
            if match_key != "id":
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        "federation-entry-inspect must use match_key 'id'",
                    )
                )
        elif name == "federation-root-inspect":
            try:
                allowed_root_ids = ensure_string_list(
                    query.get("allowed_root_ids"),
                    f"{location}.allowed_root_ids",
                )
            except RouterError as exc:
                issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
                continue
            if allowed_root_ids != list(FEDERATION_ROOT_IDS):
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        "federation-root-inspect must advertise exactly aoa-root and tos-root",
                    )
                )
            if match_key != "id":
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        "federation-root-inspect must use match_key 'id'",
                    )
                )
        else:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"unsupported federation query '{name}'",
                )
            )

    for index, raw_starter in enumerate(federation_starters):
        location = f"tiny_model_entrypoints.json.federation_starters[{index}]"
        try:
            starter = ensure_mapping(raw_starter, location)
            starter_name = ensure_string(starter.get("name"), f"{location}.name")
            if starter_name in starter_names:
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"starter names must be unique; found duplicate '{starter_name}'",
                    )
                )
            else:
                starter_names.add(starter_name)
            source_repo = ensure_string(starter.get("source_repo"), f"{location}.source_repo")
            surface_file = ensure_repo_relative_path(
                starter.get("target_surface"),
                f"{location}.target_surface",
            )
            if source_repo != "aoa-routing" or surface_file != FEDERATION_ENTRYPOINTS_FILE:
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"federation starter '{starter_name}' must target aoa-routing/{FEDERATION_ENTRYPOINTS_FILE}",
                    )
                )
            entry_kind = starter.get("entry_kind")
            if entry_kind in FEDERATION_DECLARED_ENTRY_KINDS:
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        f"federation starter '{starter_name}' must not target a declared-but-inactive entry kind",
                    )
                )
            match_key = starter.get("match_key")
            target_value = starter.get("target_value")
        except RouterError as exc:
            issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
            continue

        if starter_name == "federation-root":
            if match_key is not None or target_value is not None:
                issues.append(
                    ValidationIssue(
                        "tiny_model_entrypoints.json",
                        "federation-root must stay as the unfiltered federation surface opener",
                    )
                )
            continue

        validate_federation_target(
            consumer_label=f"federation starter '{starter_name}'",
            location=location,
            source_repo=source_repo,
            surface_file=surface_file,
            match_key=match_key,
            target_value=target_value,
            entry_kind=entry_kind,
        )


def validate_surface_lookup_target(
    surface_file: Any,
    location: str,
    memo_root: Path,
    issues: list[ValidationIssue],
) -> str | None:
    try:
        relative_surface_path = ensure_repo_relative_path(surface_file, location)
    except RouterError as exc:
        issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
        return None
    try:
        payload = ensure_mapping(
            load_json_file(memo_root.resolve() / relative_surface_path),
            f"aoa-memo/{relative_surface_path}",
        )
        load_surface_entries_for_validation(payload, relative_surface_path)
    except RouterError as exc:
        issues.append(ValidationIssue(f"aoa-memo/{relative_surface_path}", str(exc)))
        return None
    return relative_surface_path


def validate_contract_targets_for_surface(
    *,
    contracts_by_mode: dict[str, Any],
    supported_modes: list[str],
    inspect_surface_file: str | None,
    expand_surface_file: str | None,
    memo_root: Path,
    issues: list[ValidationIssue],
    contracts_location_prefix: str,
    mode_message: str,
    inspect_message: str,
    expand_message: str,
) -> dict[str, dict[str, str | None]]:
    contract_targets_by_mode: dict[str, dict[str, str | None]] = {}
    for mode, mode_contract_file in sorted(
        (
            (mode, contract_file)
            for mode, contract_file in contracts_by_mode.items()
            if isinstance(mode, str) and mode.strip()
        ),
        key=lambda item: item[0],
    ):
        if mode not in supported_modes:
            continue
        try:
            relative_contract_path = ensure_repo_relative_path(
                mode_contract_file,
                f"{contracts_location_prefix}.{mode}",
            )
        except RouterError as exc:
            issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
            continue
        contract_path = memo_root.resolve() / relative_contract_path
        contract_location = f"aoa-memo/{relative_contract_path}"
        try:
            contract = ensure_mapping(
                load_json_file(contract_path),
                contract_location,
            )
            contract_mode = contract.get("mode")
            contract_inspect_surface = ensure_repo_relative_path(
                contract.get("inspect_surface"),
                f"{contract_location}.inspect_surface",
            )
            contract_expand_surface = ensure_repo_relative_path(
                contract.get("expand_surface"),
                f"{contract_location}.expand_surface",
            )
            contract_capsule_surface = contract.get("capsule_surface")
            if contract_capsule_surface is not None:
                contract_capsule_surface = ensure_repo_relative_path(
                    contract_capsule_surface,
                    f"{contract_location}.capsule_surface",
                )
        except RouterError as exc:
            issues.append(ValidationIssue(contract_location, str(exc)))
            continue
        if contract_mode != mode:
            issues.append(ValidationIssue(contract_location, mode_message))
        if contract_inspect_surface != inspect_surface_file:
            issues.append(ValidationIssue(contract_location, inspect_message))
        if contract_expand_surface != expand_surface_file:
            issues.append(ValidationIssue(contract_location, expand_message))
        contract_targets_by_mode[mode] = {
            "contract_file": relative_contract_path,
            "inspect_surface": contract_inspect_surface,
            "expand_surface": contract_expand_surface,
            "capsule_surface": contract_capsule_surface,
        }
    return contract_targets_by_mode


def validate_capsule_surfaces_by_mode(
    *,
    capsule_surfaces_by_mode: Any,
    supported_modes: list[str],
    contract_targets_by_mode: dict[str, dict[str, str | None]],
    required_capsule_modes: Iterable[str],
    memo_root: Path,
    issues: list[ValidationIssue],
    location_prefix: str,
    mapping_label: str,
    subset_message: str,
    required_contract_message: str,
    missing_mapping_message: str,
    mismatch_message: str,
    unexpected_mapping_message: str,
) -> None:
    raw_mapping: dict[str, Any]
    if capsule_surfaces_by_mode is None:
        raw_mapping = {}
    elif not isinstance(capsule_surfaces_by_mode, dict):
        issues.append(ValidationIssue("task_to_surface_hints.json", f"{mapping_label} must be an object when present"))
        return
    else:
        raw_mapping = capsule_surfaces_by_mode

    if any(not isinstance(mode, str) or not mode.strip() for mode in raw_mapping):
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"{mapping_label} keys must be non-empty strings",
            )
        )

    supported_mode_set = set(supported_modes)
    mapping_keys = sorted(mode for mode in raw_mapping if isinstance(mode, str) and mode.strip())
    unsupported_modes = sorted(set(mapping_keys) - supported_mode_set)
    if unsupported_modes:
        issues.append(ValidationIssue("task_to_surface_hints.json", subset_message))

    normalized_capsule_surfaces: dict[str, str] = {}
    for mode in mapping_keys:
        if mode not in supported_mode_set:
            continue
        surface_file = validate_surface_lookup_target(
            raw_mapping.get(mode),
            f"{location_prefix}.{mode}",
            memo_root,
            issues,
        )
        if surface_file is not None:
            normalized_capsule_surfaces[mode] = surface_file

    required_capsule_mode_set = set(required_capsule_modes)
    for mode in supported_modes:
        contract_capsule_surface = contract_targets_by_mode.get(mode, {}).get("capsule_surface")
        advertised_capsule_surface = raw_mapping.get(mode)
        if mode in required_capsule_mode_set and contract_capsule_surface is None:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    required_contract_message.format(mode=mode),
                )
            )
        if contract_capsule_surface is None:
            if advertised_capsule_surface is not None:
                issues.append(
                    ValidationIssue(
                        "task_to_surface_hints.json",
                        unexpected_mapping_message.format(mode=mode),
                    )
                )
            continue
        if advertised_capsule_surface is None:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    missing_mapping_message.format(mode=mode),
                )
            )
            continue
        if normalized_capsule_surfaces.get(mode) != contract_capsule_surface:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    mismatch_message.format(mode=mode),
                )
            )


def validate_parallel_recall_family(
    family_name: str,
    family_payload: dict[str, Any],
    memo_root: Path,
    issues: list[ValidationIssue],
) -> None:
    location_prefix = f"task_to_surface_hints.json.memo.actions.recall.parallel_families.{family_name}"
    default_mode = family_payload.get("default_mode")
    supported_modes = family_payload.get("supported_modes")
    contracts_by_mode = family_payload.get("contracts_by_mode")
    capsule_surfaces_by_mode = family_payload.get("capsule_surfaces_by_mode")

    if not isinstance(default_mode, str) or not default_mode.strip():
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' must define default_mode",
            )
        )
        return
    try:
        supported_mode_values = ensure_string_list(
            supported_modes,
            f"{location_prefix}.supported_modes",
        )
    except RouterError as exc:
        issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
        return
    if not isinstance(contracts_by_mode, dict) or not contracts_by_mode:
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' must define contracts_by_mode",
            )
        )
        return
    if default_mode not in supported_mode_values:
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' default_mode must be included in supported_modes",
            )
        )
    if any(not isinstance(mode, str) or not mode.strip() for mode in contracts_by_mode):
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' contracts_by_mode keys must be non-empty strings",
            )
        )
    mapping_keys = sorted(mode for mode in contracts_by_mode if isinstance(mode, str) and mode.strip())
    if mapping_keys != sorted(supported_mode_values):
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' contracts_by_mode keys must match supported_modes",
            )
        )

    inspect_surface_file = validate_surface_lookup_target(
        family_payload.get("inspect_surface"),
        f"{location_prefix}.inspect_surface",
        memo_root,
        issues,
    )
    expand_surface_file = validate_surface_lookup_target(
        family_payload.get("expand_surface"),
        f"{location_prefix}.expand_surface",
        memo_root,
        issues,
    )
    if inspect_surface_file != MEMO_OBJECT_INSPECT_SURFACE_FILE:
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' inspect_surface must stay {MEMO_OBJECT_INSPECT_SURFACE_FILE}",
            )
        )
    if expand_surface_file != MEMO_OBJECT_EXPAND_SURFACE_FILE:
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' expand_surface must stay {MEMO_OBJECT_EXPAND_SURFACE_FILE}",
            )
        )

    expected_modes = list(MEMO_OBJECT_RECALL_CONTRACTS_BY_MODE.keys())
    if sorted(supported_mode_values) != sorted(expected_modes):
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' supported_modes must be exactly: {', '.join(expected_modes)}",
            )
        )
    if default_mode != MEMO_OBJECT_RECALL_DEFAULT_MODE:
        issues.append(
            ValidationIssue(
                "task_to_surface_hints.json",
                f"parallel recall family '{family_name}' default_mode must stay '{MEMO_OBJECT_RECALL_DEFAULT_MODE}'",
            )
        )
    for mode, expected_contract_file in MEMO_OBJECT_RECALL_CONTRACTS_BY_MODE.items():
        actual_contract_file = contracts_by_mode.get(mode)
        if actual_contract_file != expected_contract_file:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"parallel recall family '{family_name}' contract for mode '{mode}' must stay {expected_contract_file}",
                )
            )
    if inspect_surface_file is None or expand_surface_file is None:
        return
    contract_targets_by_mode = validate_contract_targets_for_surface(
        contracts_by_mode=contracts_by_mode,
        supported_modes=supported_mode_values,
        inspect_surface_file=inspect_surface_file,
        expand_surface_file=expand_surface_file,
        memo_root=memo_root,
        issues=issues,
        contracts_location_prefix=f"{location_prefix}.contracts_by_mode",
        mode_message=(
            f"parallel recall family '{family_name}' contract mode must match its advertised recall mode"
        ),
        inspect_message=(
            f"parallel recall family '{family_name}' contract inspect_surface must match the family inspect surface"
        ),
        expand_message=(
            f"parallel recall family '{family_name}' contract expand_surface must match the family expand surface"
        ),
    )
    validate_capsule_surfaces_by_mode(
        capsule_surfaces_by_mode=capsule_surfaces_by_mode,
        supported_modes=supported_mode_values,
        contract_targets_by_mode=contract_targets_by_mode,
        required_capsule_modes=MEMO_CAPSULE_RECALL_MODES,
        memo_root=memo_root,
        issues=issues,
        location_prefix=f"{location_prefix}.capsule_surfaces_by_mode",
        mapping_label=f"parallel recall family '{family_name}' capsule_surfaces_by_mode",
        subset_message=(
            f"parallel recall family '{family_name}' capsule_surfaces_by_mode keys must be a subset of supported_modes"
        ),
        required_contract_message=(
            f"parallel recall family '{family_name}' contract for mode '{{mode}}' must define capsule_surface for inspect -> capsule -> expand routing"
        ),
        missing_mapping_message=(
            f"parallel recall family '{family_name}' capsule_surfaces_by_mode must include mode '{{mode}}'"
        ),
        mismatch_message=(
            f"parallel recall family '{family_name}' contract capsule_surface must match capsule_surfaces_by_mode for mode '{{mode}}'"
        ),
        unexpected_mapping_message=(
            f"parallel recall family '{family_name}' capsule_surfaces_by_mode advertises mode '{{mode}}' but its contract does not define capsule_surface"
        ),
    )


def validate_recall_targets(
    hints_payload: dict[str, Any],
    memo_root: Path,
    issues: list[ValidationIssue],
) -> None:
    try:
        hints = ensure_list(hints_payload.get("hints"), "task_to_surface_hints.json.hints")
        memo_surfaces = load_memo_catalog_surfaces(memo_root)
    except RouterError as exc:
        issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
        return
    declared_modes = set(collect_memo_recall_mode_order(memo_surfaces))
    for index, raw_hint in enumerate(hints):
        try:
            hint = ensure_mapping(raw_hint, f"task_to_surface_hints.json.hints[{index}]")
        except RouterError as exc:
            issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
            continue
        if hint.get("kind") != "memo" or hint.get("enabled") is not True:
            continue
        actions = hint.get("actions")
        if not isinstance(actions, dict):
            continue
        recall = actions.get("recall")
        inspect = actions.get("inspect")
        expand = actions.get("expand")
        if not isinstance(recall, dict) or not recall.get("enabled"):
            continue
        contract_file = recall.get("contract_file")
        default_mode = recall.get("default_mode")
        supported_modes = recall.get("supported_modes")
        contracts_by_mode = recall.get("contracts_by_mode")
        capsule_surfaces_by_mode = recall.get("capsule_surfaces_by_mode")
        if not isinstance(default_mode, str) or not default_mode.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    "enabled recall action for kind 'memo' must define default_mode",
                )
            )
            continue
        try:
            supported_mode_values = ensure_string_list(
                supported_modes, "task_to_surface_hints.json.memo.actions.recall.supported_modes"
            )
        except RouterError as exc:
            issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
            continue
        if not isinstance(contracts_by_mode, dict) or not contracts_by_mode:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    "enabled recall action for kind 'memo' must define contracts_by_mode",
                )
            )
            continue
        if default_mode not in supported_mode_values:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    "memo default_mode must be included in supported_modes",
                )
            )
        if any(not isinstance(mode, str) or not mode.strip() for mode in contracts_by_mode):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    "memo contracts_by_mode keys must be non-empty strings",
                )
            )
        if contract_file is not None:
            if not isinstance(contract_file, str) or not contract_file.strip():
                issues.append(
                    ValidationIssue(
                        "task_to_surface_hints.json",
                        "memo contract_file must be a non-empty string when present",
                    )
                )
            elif contracts_by_mode.get(default_mode) != contract_file:
                issues.append(
                    ValidationIssue(
                        "task_to_surface_hints.json",
                        "memo contract_file must match contracts_by_mode for default_mode",
                    )
                )
        mapping_keys = sorted(mode for mode in contracts_by_mode if isinstance(mode, str) and mode.strip())
        if mapping_keys != sorted(supported_mode_values):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    "memo contracts_by_mode keys must match supported_modes",
                )
            )
        unsupported_modes = sorted(set(supported_mode_values) - declared_modes)
        if unsupported_modes:
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"memo supported_modes must exist in aoa-memo/{MEMO_INSPECT_SURFACE_FILE}: {', '.join(unsupported_modes)}",
                )
            )
        inspect_surface_file = inspect.get("surface_file") if isinstance(inspect, dict) else None
        expand_surface_file = expand.get("surface_file") if isinstance(expand, dict) else None
        contract_targets_by_mode = validate_contract_targets_for_surface(
            contracts_by_mode=contracts_by_mode,
            supported_modes=supported_mode_values,
            inspect_surface_file=inspect_surface_file if isinstance(inspect_surface_file, str) else None,
            expand_surface_file=expand_surface_file if isinstance(expand_surface_file, str) else None,
            memo_root=memo_root,
            issues=issues,
            contracts_location_prefix="task_to_surface_hints.json.memo.actions.recall.contracts_by_mode",
            mode_message="recall contract mode must match its advertised recall mode",
            inspect_message="recall contract inspect_surface must match the memo inspect surface hint",
            expand_message="recall contract expand_surface must match the memo expand surface hint",
        )
        validate_capsule_surfaces_by_mode(
            capsule_surfaces_by_mode=capsule_surfaces_by_mode,
            supported_modes=supported_mode_values,
            contract_targets_by_mode=contract_targets_by_mode,
            required_capsule_modes=MEMO_CAPSULE_RECALL_MODES,
            memo_root=memo_root,
            issues=issues,
            location_prefix="task_to_surface_hints.json.memo.actions.recall.capsule_surfaces_by_mode",
            mapping_label="memo capsule_surfaces_by_mode",
            subset_message="memo capsule_surfaces_by_mode keys must be a subset of supported_modes",
            required_contract_message=(
                "recall contract for mode '{mode}' must define capsule_surface for router-ready inspect -> capsule -> expand routing"
            ),
            missing_mapping_message="memo capsule_surfaces_by_mode must include mode '{mode}'",
            mismatch_message=(
                "recall contract capsule_surface must match memo capsule_surfaces_by_mode for mode '{mode}'"
            ),
            unexpected_mapping_message=(
                "memo capsule_surfaces_by_mode advertises mode '{mode}' but its recall contract does not define capsule_surface"
            ),
        )
        parallel_families = recall.get("parallel_families")
        if parallel_families is None:
            continue
        if not isinstance(parallel_families, dict):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    "memo parallel_families must be an object when present",
                )
            )
            continue
        for family_name, raw_family in sorted(parallel_families.items()):
            try:
                family_payload = ensure_mapping(
                    raw_family,
                    f"task_to_surface_hints.json.memo.actions.recall.parallel_families.{family_name}",
                )
            except RouterError as exc:
                issues.append(ValidationIssue("task_to_surface_hints.json", str(exc)))
                continue
            validate_parallel_recall_family(family_name, family_payload, memo_root, issues)


def payload_contains_key(payload: Any, target_key: str) -> bool:
    if isinstance(payload, dict):
        if target_key in payload:
            return True
        return any(payload_contains_key(value, target_key) for value in payload.values())
    if isinstance(payload, list):
        return any(payload_contains_key(item, target_key) for item in payload)
    return False


def validate_task_tier_hints(
    tier_hints_payload: dict[str, Any],
    agents_root: Path,
    issues: list[ValidationIssue],
) -> None:
    try:
        source_of_truth = ensure_mapping(
            tier_hints_payload.get("source_of_truth"),
            "task_to_tier_hints.json.source_of_truth",
        )
    except RouterError as exc:
        issues.append(ValidationIssue("task_to_tier_hints.json", str(exc)))
        return

    source_repo = source_of_truth.get("tier_registry_repo")
    if source_repo != MODEL_TIER_SOURCE_REPO:
        issues.append(
            ValidationIssue(
                "task_to_tier_hints.json",
                f"tier source repo must stay '{MODEL_TIER_SOURCE_REPO}'",
            )
        )
        return

    try:
        registry_relative_path = ensure_repo_relative_path(
            source_of_truth.get("tier_registry_path"),
            "task_to_tier_hints.json.source_of_truth.tier_registry_path",
        )
        _, tier_index = load_model_tier_registry(agents_root, registry_relative_path)
        hints = ensure_list(tier_hints_payload.get("hints"), "task_to_tier_hints.json.hints")
    except RouterError as exc:
        issues.append(ValidationIssue("task_to_tier_hints.json", str(exc)))
        return

    seen_task_families: set[str] = set()
    for index, raw_hint in enumerate(hints):
        location = f"task_to_tier_hints.json.hints[{index}]"
        try:
            hint = ensure_mapping(raw_hint, location)
        except RouterError as exc:
            issues.append(ValidationIssue("task_to_tier_hints.json", str(exc)))
            continue

        task_family = hint.get("task_family")
        if isinstance(task_family, str):
            if task_family in seen_task_families:
                issues.append(
                    ValidationIssue(
                        "task_to_tier_hints.json",
                        f"duplicate task_family '{task_family}' in task_to_tier_hints.json",
                    )
                )
            else:
                seen_task_families.add(task_family)

        preferred_tier = hint.get("preferred_tier")
        if isinstance(preferred_tier, str):
            preferred_entry = tier_index.get(preferred_tier)
            if preferred_entry is None:
                issues.append(
                    ValidationIssue(
                        "task_to_tier_hints.json",
                        f"{location}.preferred_tier references unknown tier '{preferred_tier}'",
                    )
                )
            elif hint.get("output_artifact") != preferred_entry["artifact_requirement"]:
                issues.append(
                    ValidationIssue(
                        "task_to_tier_hints.json",
                        f"{location}.output_artifact must match artifact_requirement for tier '{preferred_tier}'",
                    )
                )

        fallback_tier = hint.get("fallback_tier")
        if isinstance(fallback_tier, str) and fallback_tier not in tier_index:
            issues.append(
                ValidationIssue(
                    "task_to_tier_hints.json",
                    f"{location}.fallback_tier references unknown tier '{fallback_tier}'",
                )
            )


def validate_generated_outputs(
    generated_dir: Path,
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
    agents_root: Path,
    aoa_root: Path,
    playbooks_root: Path,
    kag_root: Path,
    tos_root: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    generated_dir = generated_dir.resolve()
    validate_local_questbook_surfaces(REPO_ROOT, issues)

    registry_path = generated_dir / "cross_repo_registry.min.json"
    router_path = generated_dir / "aoa_router.min.json"
    hints_path = generated_dir / "task_to_surface_hints.json"
    tier_hints_path = generated_dir / "task_to_tier_hints.json"
    quest_dispatch_hints_path = generated_dir / Path(QUEST_DISPATCH_HINTS_FILE).name
    federation_entrypoints_path = generated_dir / Path(FEDERATION_ENTRYPOINTS_FILE).name
    return_navigation_path = generated_dir / Path(RETURN_NAVIGATION_HINTS_FILE).name
    recommended_path = generated_dir / "recommended_paths.min.json"
    relation_hints_path = generated_dir / "kag_source_lift_relation_hints.min.json"
    pairing_path = generated_dir / "pairing_hints.min.json"
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"
    two_stage_entrypoints_path = generated_dir / "two_stage_skill_entrypoints.json"
    two_stage_prompt_blocks_path = generated_dir / "two_stage_router_prompt_blocks.json"
    two_stage_tool_schemas_path = generated_dir / "two_stage_router_tool_schemas.json"
    two_stage_examples_path = generated_dir / "two_stage_router_examples.json"
    two_stage_manifest_path = generated_dir / "two_stage_router_manifest.json"

    registry_payload = load_output(registry_path, issues)
    router_payload = load_output(router_path, issues)
    hints_payload = load_output(hints_path, issues)
    tier_hints_payload = load_output(tier_hints_path, issues)
    quest_dispatch_hints_payload = load_output(quest_dispatch_hints_path, issues)
    federation_entrypoints_payload = load_output(federation_entrypoints_path, issues)
    return_navigation_payload = load_output(return_navigation_path, issues)
    recommended_payload = load_output(recommended_path, issues)
    relation_hints_payload = load_output(relation_hints_path, issues)
    pairing_payload = load_output(pairing_path, issues)
    tiny_model_payload = load_output(tiny_model_path, issues)
    two_stage_entrypoints_payload = load_output(two_stage_entrypoints_path, issues)
    two_stage_prompt_blocks_payload = load_output(two_stage_prompt_blocks_path, issues)
    two_stage_tool_schemas_payload = load_output(two_stage_tool_schemas_path, issues)
    two_stage_examples_payload = load_output(two_stage_examples_path, issues)
    two_stage_manifest_payload = load_output(two_stage_manifest_path, issues)
    if any(
        payload is None
        for payload in (
            registry_payload,
            router_payload,
            hints_payload,
            tier_hints_payload,
            quest_dispatch_hints_payload,
            federation_entrypoints_payload,
            return_navigation_payload,
            recommended_payload,
            relation_hints_payload,
            pairing_payload,
            tiny_model_payload,
            two_stage_entrypoints_payload,
            two_stage_prompt_blocks_payload,
            two_stage_tool_schemas_payload,
            two_stage_examples_payload,
            two_stage_manifest_payload,
        )
    ):
        return issues

    validate_rebuild_parity(
        {
            registry_path.name: registry_payload,
            router_path.name: router_payload,
            hints_path.name: hints_payload,
            tier_hints_path.name: tier_hints_payload,
            quest_dispatch_hints_path.name: quest_dispatch_hints_payload,
            federation_entrypoints_path.name: federation_entrypoints_payload,
            return_navigation_path.name: return_navigation_payload,
            recommended_path.name: recommended_payload,
            relation_hints_path.name: relation_hints_payload,
            pairing_path.name: pairing_payload,
            tiny_model_path.name: tiny_model_payload,
            two_stage_entrypoints_path.name: two_stage_entrypoints_payload,
            two_stage_prompt_blocks_path.name: two_stage_prompt_blocks_payload,
            two_stage_tool_schemas_path.name: two_stage_tool_schemas_payload,
            two_stage_examples_path.name: two_stage_examples_payload,
            two_stage_manifest_path.name: two_stage_manifest_payload,
        },
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        agents_root,
        aoa_root,
        playbooks_root,
        kag_root,
        tos_root,
        issues,
    )

    for output_path, payload in (
        (registry_path, registry_payload),
        (router_path, router_payload),
        (hints_path, hints_payload),
        (tier_hints_path, tier_hints_payload),
        (quest_dispatch_hints_path, quest_dispatch_hints_payload),
        (federation_entrypoints_path, federation_entrypoints_payload),
        (return_navigation_path, return_navigation_payload),
        (recommended_path, recommended_payload),
        (relation_hints_path, relation_hints_payload),
        (pairing_path, pairing_payload),
        (tiny_model_path, tiny_model_payload),
        (two_stage_entrypoints_path, two_stage_entrypoints_payload),
        (two_stage_prompt_blocks_path, two_stage_prompt_blocks_payload),
        (two_stage_tool_schemas_path, two_stage_tool_schemas_payload),
        (two_stage_examples_path, two_stage_examples_payload),
        (two_stage_manifest_path, two_stage_manifest_payload),
    ):
        validate_against_schema(
            payload,
            OUTPUT_SCHEMA_NAMES[output_path.name],
            output_path.name,
            issues,
        )

    try:
        registry_entries = ensure_list(registry_payload.get("entries"), f"{registry_path.name}.entries")
    except RouterError as exc:
        issues.append(ValidationIssue(registry_path.name, str(exc)))
        return issues

    technique_catalog_source, technique_catalog_entries = load_technique_catalog_entries(
        techniques_root
    )

    normalized_registry_entries: list[dict[str, Any]] = []
    dependency_safe_registry_entries: list[dict[str, Any]] = []
    projection_safe_registry_entries: list[dict[str, Any]] = []
    recommended_safe_registry_entries: list[dict[str, Any]] = []
    seen_registry_keys: set[tuple[str, str]] = set()
    for index, raw_entry in enumerate(registry_entries):
        location = f"{registry_path.name}.entries[{index}]"
        try:
            entry = ensure_mapping(raw_entry, location)
        except RouterError as exc:
            issues.append(ValidationIssue(registry_path.name, str(exc)))
            continue
        schema_issue_count = len(issues)
        validate_against_schema(entry, "router-entry.schema.json", location, issues)
        schema_valid = len(issues) == schema_issue_count
        key = registry_entry_key(entry)
        if key is not None:
            if key in seen_registry_keys:
                issues.append(ValidationIssue(location, f"duplicate registry entry for {key[0]}:{key[1]}"))
            else:
                seen_registry_keys.add(key)
        if entry.get("kind") not in ALL_KINDS:
            issues.append(ValidationIssue(location, f"invalid kind '{entry.get('kind')}'"))
        if entry.get("kind") in ACTIVE_KINDS and entry.get("source_type") != "generated-catalog":
            issues.append(
                ValidationIssue(
                    location,
                    "active registry entries must use source_type 'generated-catalog'",
                )
            )
        validate_entry_repo_and_path(entry, location, issues)
        attributes_valid = validate_registry_entry_attributes(entry, location, issues)
        normalized_registry_entries.append(entry)
        if attributes_valid:
            dependency_safe_registry_entries.append(entry)
        if schema_valid and is_projection_safe_registry_entry(entry):
            projection_safe_registry_entries.append(entry)
            if entry.get("kind") not in {"skill", "eval"} or attributes_valid:
                recommended_safe_registry_entries.append(entry)

    validate_registry_dependencies(
        normalized_registry_entries,
        dependency_safe_registry_entries,
        issues,
    )

    try:
        router_entries = ensure_list(router_payload.get("entries"), f"{router_path.name}.entries")
    except RouterError as exc:
        issues.append(ValidationIssue(router_path.name, str(exc)))
        return issues

    normalized_router_entries: list[dict[str, Any]] = []
    seen_router_keys: set[tuple[str, str]] = set()
    for index, raw_entry in enumerate(router_entries):
        location = f"{router_path.name}.entries[{index}]"
        try:
            entry = ensure_mapping(raw_entry, location)
        except RouterError as exc:
            issues.append(ValidationIssue(router_path.name, str(exc)))
            continue
        validate_against_schema(entry, "router-entry.schema.json", location, issues)
        key = registry_entry_key(entry)
        if key is not None:
            if key in seen_router_keys:
                issues.append(ValidationIssue(location, f"duplicate router entry for {key[0]}:{key[1]}"))
            else:
                seen_router_keys.add(key)
        if "source_type" in entry or "attributes" in entry:
            issues.append(ValidationIssue(location, "router entries must stay as the thin projection surface"))
        validate_entry_repo_and_path(entry, location, issues)
        normalized_router_entries.append(entry)

    if router_payload != build_router_payload(projection_safe_registry_entries):
        issues.append(ValidationIssue(router_path.name, "aoa_router.min.json does not match the registry projection"))

    if hints_payload != build_task_to_surface_hints_payload(memo_root):
        issues.append(ValidationIssue(hints_path.name, "task_to_surface_hints.json does not match the expected static dispatch surface"))
    try:
        expected_tier_hints_payload = build_task_to_tier_hints_payload(agents_root)
    except RouterError as exc:
        issues.append(
            ValidationIssue(
                tier_hints_path.name,
                f"could not rebuild task_to_tier_hints.json from aoa-agents: {exc}",
            )
        )
    else:
        if tier_hints_payload != expected_tier_hints_payload:
            issues.append(ValidationIssue(tier_hints_path.name, "task_to_tier_hints.json does not match the expected static tier dispatch surface"))
    validate_task_tier_hints(tier_hints_payload, agents_root, issues)
    expected_quest_dispatch_hints_payload: dict[str, Any] | None = None
    try:
        expected_quest_dispatch_hints_payload = build_quest_dispatch_hints_payload(
            techniques_root,
            skills_root,
            evals_root,
        )
    except RouterError as exc:
        issues.append(
            ValidationIssue(
                quest_dispatch_hints_path.name,
                f"could not rebuild {quest_dispatch_hints_path.name} from live source/proof quest surfaces: {exc}",
            )
        )
    else:
        if quest_dispatch_hints_payload != expected_quest_dispatch_hints_payload:
            issues.append(
                ValidationIssue(
                    quest_dispatch_hints_path.name,
                    f"{quest_dispatch_hints_path.name} does not match the expected live source-only quest routing surface",
                )
            )
    expected_federation_entrypoints_payload: dict[str, Any] | None = None
    try:
        expected_federation_entrypoints_payload = build_federation_entrypoints_payload(
            aoa_root,
            techniques_root,
            agents_root,
            playbooks_root,
            kag_root,
            tos_root,
        )
    except RouterError as exc:
        issues.append(
            ValidationIssue(
                federation_entrypoints_path.name,
                f"could not rebuild {federation_entrypoints_path.name} from sibling source surfaces: {exc}",
            )
        )
    else:
        if federation_entrypoints_payload != expected_federation_entrypoints_payload:
            issues.append(
                ValidationIssue(
                    federation_entrypoints_path.name,
                    "federation_entrypoints.min.json does not match the expected federation entry ABI surface",
                )
            )
    canonical_federation_entrypoints_payload = (
        expected_federation_entrypoints_payload or federation_entrypoints_payload
    )
    validate_federation_entrypoints(
        federation_entrypoints_payload,
        generated_dir,
        techniques_root,
        agents_root,
        playbooks_root,
        kag_root,
        aoa_root,
        tos_root,
        issues,
    )
    validate_quest_dispatch_hints(
        quest_dispatch_hints_payload,
        techniques_root,
        skills_root,
        evals_root,
        canonical_federation_entrypoints_payload,
        issues,
    )
    expected_return_navigation_payload: dict[str, Any] | None = None
    try:
        expected_return_navigation_payload = build_return_navigation_hints_payload(
            techniques_root,
            skills_root,
            evals_root,
            memo_root,
            aoa_root,
            agents_root,
            playbooks_root,
            kag_root,
            tos_root,
            hints_payload,
            canonical_federation_entrypoints_payload,
        )
    except RouterError as exc:
        issues.append(
            ValidationIssue(
                return_navigation_path.name,
                f"could not rebuild {return_navigation_path.name} from sibling source surfaces: {exc}",
            )
        )
    else:
        if return_navigation_payload != expected_return_navigation_payload:
            issues.append(
                ValidationIssue(
                    return_navigation_path.name,
                    f"{return_navigation_path.name} does not match the expected recurrence re-entry surface",
                )
            )
    validate_return_navigation_hints(
        return_navigation_payload,
        generated_dir,
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        agents_root,
        aoa_root,
        playbooks_root,
        kag_root,
        tos_root,
        issues,
    )
    validate_inspect_targets(
        projection_safe_registry_entries,
        hints_payload,
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        issues,
    )
    validate_expand_targets(
        projection_safe_registry_entries,
        hints_payload,
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        issues,
    )
    validate_pair_targets(
        projection_safe_registry_entries,
        hints_payload,
        generated_dir,
        issues,
    )
    validate_recall_targets(hints_payload, memo_root, issues)

    try:
        recommended_entries = ensure_list(
            recommended_payload.get("entries"),
            f"{recommended_path.name}.entries",
        )
    except RouterError as exc:
        issues.append(ValidationIssue(recommended_path.name, str(exc)))
        return issues

    for index, raw_entry in enumerate(recommended_entries):
        location = f"{recommended_path.name}.entries[{index}]"
        try:
            entry = ensure_mapping(raw_entry, location)
        except RouterError as exc:
            issues.append(ValidationIssue(recommended_path.name, str(exc)))
            continue
        for edge_name in ("upstream", "downstream"):
            edges = entry.get(edge_name)
            if not isinstance(edges, list):
                issues.append(ValidationIssue(location, f"{edge_name} must be a list"))
                continue
            for hop_index, raw_hop in enumerate(edges):
                hop_location = f"{location}.{edge_name}[{hop_index}]"
                if not isinstance(raw_hop, dict):
                    issues.append(ValidationIssue(hop_location, "hop must be an object"))
                    continue
                if raw_hop.get("relation") not in {"requires", "required_by"}:
                    issues.append(ValidationIssue(hop_location, "relation must be 'requires' or 'required_by'"))
                if raw_hop.get("kind") not in RECOMMENDED_HOP_KINDS:
                    issues.append(ValidationIssue(hop_location, "hop kind must be technique, skill, or eval"))
                if raw_hop.get("kind") == entry.get("kind"):
                    issues.append(ValidationIssue(hop_location, "same-kind hops are not allowed in the bounded recommended path surface"))

    try:
        expected_recommended = build_recommended_paths_payload(recommended_safe_registry_entries)
    except RouterError as exc:
        issues.append(ValidationIssue(recommended_path.name, str(exc)))
    else:
        if recommended_payload != expected_recommended:
            issues.append(ValidationIssue(recommended_path.name, "recommended_paths.min.json does not match registry-derived dependencies"))

    try:
        expected_pairing = build_pairing_hints_payload(
            recommended_safe_registry_entries,
            technique_catalog_source,
            technique_catalog_entries,
        )
    except RouterError as exc:
        issues.append(ValidationIssue(pairing_path.name, str(exc)))
    else:
        if pairing_payload != expected_pairing:
            issues.append(
                ValidationIssue(
                    pairing_path.name,
                    "pairing_hints.min.json does not match the bounded pairing derivation",
                )
            )

    try:
        expected_relation_hints = build_kag_source_lift_relation_hints_payload(
            normalized_registry_entries,
            technique_catalog_source,
            technique_catalog_entries,
        )
    except RouterError as exc:
        issues.append(ValidationIssue(relation_hints_path.name, str(exc)))
    else:
        if relation_hints_payload != expected_relation_hints:
            issues.append(
                ValidationIssue(
                    relation_hints_path.name,
                    "kag_source_lift_relation_hints.min.json does not match the live direct relation surface",
                )
            )

    try:
        expected_tiny_model_payload = build_tiny_model_entrypoints_payload(
            projection_safe_registry_entries,
            hints_payload,
            canonical_federation_entrypoints_payload,
        )
    except RouterError as exc:
        issues.append(ValidationIssue(tiny_model_path.name, str(exc)))
    else:
        if tiny_model_payload != expected_tiny_model_payload:
            issues.append(
                ValidationIssue(
                    tiny_model_path.name,
                    "tiny_model_entrypoints.json does not match the expected tiny-model entry surface",
                )
            )
    validate_tiny_model_entrypoints(
        tiny_model_payload,
        generated_dir,
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        agents_root,
        playbooks_root,
        kag_root,
        aoa_root,
        tos_root,
        issues,
    )

    for filename, payload in (
        (registry_path.name, registry_payload),
        (router_path.name, router_payload),
        (hints_path.name, hints_payload),
        (tier_hints_path.name, tier_hints_payload),
        (quest_dispatch_hints_path.name, quest_dispatch_hints_payload),
        (federation_entrypoints_path.name, federation_entrypoints_payload),
        (recommended_path.name, recommended_payload),
        (relation_hints_path.name, relation_hints_payload),
        (pairing_path.name, pairing_payload),
        (tiny_model_path.name, tiny_model_payload),
        (two_stage_entrypoints_path.name, two_stage_entrypoints_payload),
        (two_stage_prompt_blocks_path.name, two_stage_prompt_blocks_payload),
        (two_stage_tool_schemas_path.name, two_stage_tool_schemas_payload),
        (two_stage_manifest_path.name, two_stage_manifest_payload),
    ):
        for key in SOURCE_OWNED_PAYLOAD_KEYS:
            if payload_contains_key(payload, key):
                issues.append(
                    ValidationIssue(
                        filename,
                        f"routing outputs must not copy source-owned payload key '{key}'",
                    )
                )

    for location, message in validate_two_stage_outputs(generated_dir, skills_root):
        issues.append(ValidationIssue(location, message))

    return issues


def main() -> int:
    args = parse_args()
    issues = [
        ValidationIssue(location, message)
        for location, message in validate_nested_agents.run_validation(REPO_ROOT)
    ]
    issues.extend(
        validate_generated_outputs(
            args.generated_dir,
            args.techniques_root,
            args.skills_root,
            args.evals_root,
            args.memo_root,
            args.agents_root,
            args.aoa_root,
            args.playbooks_root,
            args.kag_root,
            args.tos_root,
        )
    )
    if issues:
        for issue in issues:
            print(f"[error] {issue.location}: {issue.message}")
        return 1
    print("[ok] validated nested AGENTS docs")
    print("[ok] validated local questbook routing seam")
    print("[ok] validated generated routing outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
