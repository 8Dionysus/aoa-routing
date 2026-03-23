#!/usr/bin/env python3
"""Validate aoa-routing generated surfaces."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from build_router import build_outputs
from router_core import (
    ACTIVE_KINDS,
    ALL_KINDS,
    CANONICAL_REPO_BY_KIND,
    DIRECT_RELATION_TYPES_SET,
    KAG_SOURCE_LIFT_TECHNIQUE_SET,
    MODEL_TIER_SOURCE_REPO,
    PAIRABLE_KINDS,
    PAIRING_SURFACE_REPO,
    RECOMMENDED_HOP_KINDS,
    REPO_ROOT,
    RESERVED_KINDS,
    RouterError,
    build_kag_source_lift_relation_hints_payload,
    build_pairing_hints_payload,
    build_recommended_paths_payload,
    build_router_payload,
    build_tiny_model_entrypoints_payload,
    build_task_to_tier_hints_payload,
    build_task_to_surface_hints_payload,
    collect_memo_recall_mode_order,
    ensure_list,
    ensure_mapping,
    ensure_repo_relative_path,
    ensure_string_list,
    is_pending_technique_id,
    load_json_file,
    load_memo_catalog_surfaces,
    load_model_tier_registry,
    load_technique_catalog_entries,
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
    "recommended_paths.min.json": "recommended-paths.schema.json",
    "kag_source_lift_relation_hints.min.json": "kag-source-lift-relation-hints.schema.json",
    "pairing_hints.min.json": "pairing-hints.schema.json",
    "tiny_model_entrypoints.json": "tiny-model-entrypoints.schema.json",
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


def validate_rebuild_parity(
    outputs: dict[str, dict[str, Any]],
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
    agents_root: Path,
    issues: list[ValidationIssue],
) -> None:
    try:
        expected_outputs = build_outputs(
            techniques_root.resolve(),
            skills_root.resolve(),
            evals_root.resolve(),
            memo_root.resolve(),
            agents_root.resolve(),
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
    array_key_by_filename = {
        "aoa_router.min.json": "entries",
        "pairing_hints.min.json": "entries",
        "technique_capsules.json": "techniques",
        "skill_capsules.json": "skills",
        "eval_capsules.json": "evals",
        "memory_catalog.min.json": "memo_surfaces",
        "technique_sections.full.json": "techniques",
        "skill_sections.full.json": "skills",
        "eval_sections.full.json": "evals",
        "memory_sections.full.json": "memo_surfaces",
    }
    key = array_key_by_filename.get(Path(surface_file).name)
    if key is None:
        raise RouterError(f"unsupported surface file '{surface_file}' for validation lookup")
    return ensure_list(payload.get(key), f"{surface_file}.{key}")


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

    route_root = generated_dir.resolve().parent
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

        if surface_file not in loaded_payloads:
            surface_path = route_root / surface_file
            location = f"aoa-routing/{surface_file}"
            try:
                loaded_payloads[surface_file] = ensure_mapping(load_json_file(surface_path), location)
            except RouterError as exc:
                issues.append(ValidationIssue(location, str(exc)))
                continue

        payload = loaded_payloads[surface_file]
        try:
            pair_entries = load_surface_entries_for_validation(payload, surface_file)
        except RouterError as exc:
            issues.append(ValidationIssue(f"aoa-routing/{surface_file}", str(exc)))
            continue

        if surface_file in validated_surface_files:
            continue
        validated_surface_files.add(surface_file)

        for pair_index, raw_entry in enumerate(pair_entries):
            location = f"aoa-routing/{surface_file}.entries[{pair_index}]"
            try:
                entry = ensure_mapping(raw_entry, location)
            except RouterError as exc:
                issues.append(ValidationIssue(f"aoa-routing/{surface_file}", str(exc)))
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
    issues: list[ValidationIssue],
) -> None:
    route_root = generated_dir.resolve().parent
    roots = {
        "aoa-routing": route_root,
        "aoa-techniques": techniques_root.resolve(),
        "aoa-skills": skills_root.resolve(),
        "aoa-evals": evals_root.resolve(),
        "aoa-memo": memo_root.resolve(),
    }

    try:
        queries = ensure_list(tiny_payload.get("queries"), "tiny_model_entrypoints.json.queries")
        starters = ensure_list(tiny_payload.get("starters"), "tiny_model_entrypoints.json.starters")
    except RouterError as exc:
        issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
        return

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
        surface_path = surface_root / surface_file
        location = f"{source_repo}/{surface_file}"
        try:
            return ensure_mapping(load_json_file(surface_path), location)
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
            return None

    for index, raw_query in enumerate(queries):
        location = f"tiny_model_entrypoints.json.queries[{index}]"
        try:
            query = ensure_mapping(raw_query, location)
            source_repo = query.get("source_repo")
            surface_file = query.get("target_surface")
            if not isinstance(source_repo, str) or not isinstance(surface_file, str):
                continue
            load_target_payload(source_repo, surface_file)
        except RouterError as exc:
            issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))

    for index, raw_starter in enumerate(starters):
        location = f"tiny_model_entrypoints.json.starters[{index}]"
        try:
            starter = ensure_mapping(raw_starter, location)
        except RouterError as exc:
            issues.append(ValidationIssue("tiny_model_entrypoints.json", str(exc)))
            continue
        source_repo = starter.get("source_repo")
        surface_file = starter.get("target_surface")
        match_key = starter.get("match_key")
        target_value = starter.get("target_value")
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
        found = False
        for raw_entry in entries:
            if not isinstance(raw_entry, dict):
                continue
            if raw_entry.get(match_key) == target_value:
                found = True
                break
        if not found:
            issues.append(
                ValidationIssue(
                    "tiny_model_entrypoints.json",
                    f"starter '{starter.get('name', index)}' target '{target_value}' was not found in {source_repo}/{surface_file}",
                )
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
        mapping_keys = sorted(contracts_by_mode.keys())
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
                    f"memo supported_modes must exist in aoa-memo/generated/memory_catalog.min.json: {', '.join(unsupported_modes)}",
                )
            )
        inspect_surface_file = inspect.get("surface_file") if isinstance(inspect, dict) else None
        expand_surface_file = expand.get("surface_file") if isinstance(expand, dict) else None
        for mode, mode_contract_file in sorted(contracts_by_mode.items()):
            if mode not in supported_mode_values:
                continue
            contract_path = memo_root.resolve() / mode_contract_file
            try:
                contract = ensure_mapping(
                    load_json_file(contract_path),
                    f"aoa-memo/{mode_contract_file}",
                )
            except RouterError as exc:
                issues.append(ValidationIssue(f"aoa-memo/{mode_contract_file}", str(exc)))
                continue
            contract_mode = contract.get("mode")
            inspect_surface = contract.get("inspect_surface")
            expand_surface = contract.get("expand_surface")
            if contract_mode != mode:
                issues.append(
                    ValidationIssue(
                        f"aoa-memo/{mode_contract_file}",
                        "recall contract mode must match its advertised recall mode",
                    )
                )
            if inspect_surface != inspect_surface_file:
                issues.append(
                    ValidationIssue(
                        f"aoa-memo/{mode_contract_file}",
                        "recall contract inspect_surface must match the memo inspect surface hint",
                    )
                )
            if expand_surface != expand_surface_file:
                issues.append(
                    ValidationIssue(
                        f"aoa-memo/{mode_contract_file}",
                        "recall contract expand_surface must match the memo expand surface hint",
                    )
                )


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
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    generated_dir = generated_dir.resolve()

    registry_path = generated_dir / "cross_repo_registry.min.json"
    router_path = generated_dir / "aoa_router.min.json"
    hints_path = generated_dir / "task_to_surface_hints.json"
    tier_hints_path = generated_dir / "task_to_tier_hints.json"
    recommended_path = generated_dir / "recommended_paths.min.json"
    relation_hints_path = generated_dir / "kag_source_lift_relation_hints.min.json"
    pairing_path = generated_dir / "pairing_hints.min.json"
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"

    registry_payload = load_output(registry_path, issues)
    router_payload = load_output(router_path, issues)
    hints_payload = load_output(hints_path, issues)
    tier_hints_payload = load_output(tier_hints_path, issues)
    recommended_payload = load_output(recommended_path, issues)
    relation_hints_payload = load_output(relation_hints_path, issues)
    pairing_payload = load_output(pairing_path, issues)
    tiny_model_payload = load_output(tiny_model_path, issues)
    if any(
        payload is None
        for payload in (
            registry_payload,
            router_payload,
            hints_payload,
            tier_hints_payload,
            recommended_payload,
            relation_hints_payload,
            pairing_payload,
            tiny_model_payload,
        )
    ):
        return issues

    validate_rebuild_parity(
        {
            registry_path.name: registry_payload,
            router_path.name: router_payload,
            hints_path.name: hints_payload,
            tier_hints_path.name: tier_hints_payload,
            recommended_path.name: recommended_payload,
            relation_hints_path.name: relation_hints_payload,
            pairing_path.name: pairing_payload,
            tiny_model_path.name: tiny_model_payload,
        },
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        agents_root,
        issues,
    )

    for output_path, payload in (
        (registry_path, registry_payload),
        (router_path, router_payload),
        (hints_path, hints_payload),
        (tier_hints_path, tier_hints_payload),
        (recommended_path, recommended_payload),
        (relation_hints_path, relation_hints_payload),
        (pairing_path, pairing_payload),
        (tiny_model_path, tiny_model_payload),
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
        issues,
    )

    for filename, payload in (
        (registry_path.name, registry_payload),
        (router_path.name, router_payload),
        (hints_path.name, hints_payload),
        (tier_hints_path.name, tier_hints_payload),
        (recommended_path.name, recommended_payload),
        (relation_hints_path.name, relation_hints_payload),
        (pairing_path.name, pairing_payload),
        (tiny_model_path.name, tiny_model_payload),
    ):
        for key in SOURCE_OWNED_PAYLOAD_KEYS:
            if payload_contains_key(payload, key):
                issues.append(
                    ValidationIssue(
                        filename,
                        f"routing outputs must not copy source-owned payload key '{key}'",
                    )
                )

    return issues


def main() -> int:
    args = parse_args()
    issues = validate_generated_outputs(
        args.generated_dir,
        args.techniques_root,
        args.skills_root,
        args.evals_root,
        args.memo_root,
        args.agents_root,
    )
    if issues:
        for issue in issues:
            print(f"[error] {issue.location}: {issue.message}")
        return 1
    print("[ok] validated generated routing outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
