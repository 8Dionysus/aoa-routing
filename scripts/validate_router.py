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

from router_core import (
    ACTIVE_KINDS,
    ALL_KINDS,
    REPO_ROOT,
    RESERVED_KINDS,
    RouterError,
    build_recommended_paths_payload,
    build_router_payload,
    build_task_to_surface_hints_payload,
    ensure_list,
    ensure_mapping,
    ensure_string_list,
    is_pending_technique_id,
    load_json_file,
)


@dataclass(frozen=True)
class ValidationIssue:
    location: str
    message: str


OUTPUT_SCHEMA_NAMES = {
    "cross_repo_registry.min.json": "cross-repo-registry.schema.json",
    "aoa_router.min.json": "aoa-router.schema.json",
    "task_to_surface_hints.json": "task-to-surface-hints.schema.json",
    "recommended_paths.min.json": "recommended-paths.schema.json",
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
    raise RouterError(f"capsule surfaces do not support kind '{kind}' in v0.1")


def section_array_key(kind: str) -> str:
    if kind == "technique":
        return "techniques"
    if kind == "skill":
        return "skills"
    if kind == "eval":
        return "evals"
    raise RouterError(f"section surfaces do not support kind '{kind}' in v0.1")


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
        if not hint["enabled"]:
            continue
        actions = hint.get("actions")
        if not isinstance(actions, dict):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"hint for kind '{hint['kind']}' must define actions",
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
                    f"hint for kind '{hint.get('kind')}' has an invalid source_repo",
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
                    f"enabled inspect action for kind '{hint.get('kind')}' must define surface_file",
                )
            )
            continue
        if not isinstance(match_field, str) or not match_field.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled inspect action for kind '{hint.get('kind')}' must define match_field",
                )
            )
            continue
        surface_path = source_root / surface_file
        location = f"{source_repo}/{surface_file}"
        try:
            payload = ensure_mapping(load_json_file(surface_path), location)
            entries = ensure_list(payload.get(capsule_array_key(hint["kind"])), location)
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
                        f"duplicate inspect match '{match_value}' for kind '{hint['kind']}'",
                    )
                )
            seen_matches.add(match_value)

        expected_matches = {
            entry["id"] if match_field == "id" else entry["name"]
            for entry in registry_entries
            if entry["kind"] == hint["kind"]
        }
        missing_matches = sorted(expected_matches - seen_matches)
        for match_value in missing_matches:
            issues.append(
                ValidationIssue(
                    location,
                    f"inspect surface is missing {hint['kind']} match '{match_value}'",
                )
            )
        unexpected_matches = sorted(seen_matches - expected_matches)
        for match_value in unexpected_matches:
            issues.append(
                ValidationIssue(
                    location,
                    f"inspect surface contains unexpected {hint['kind']} match '{match_value}'",
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
        if not hint["enabled"]:
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
                    f"hint for kind '{hint.get('kind')}' has an invalid source_repo",
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
                    f"enabled expand action for kind '{hint.get('kind')}' must define surface_file",
                )
            )
            continue
        if not isinstance(match_field, str) or not match_field.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{hint.get('kind')}' must define match_field",
                )
            )
            continue
        if not isinstance(section_key_field, str) or not section_key_field.strip():
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{hint.get('kind')}' must define section_key_field",
                )
            )
            continue
        if not isinstance(default_sections, list) or not all(
            isinstance(section, str) and section.strip() for section in default_sections
        ):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{hint.get('kind')}' must define default_sections as a string list",
                )
            )
            continue
        if not isinstance(supported_sections, list) or not all(
            isinstance(section, str) and section.strip() for section in supported_sections
        ):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"enabled expand action for kind '{hint.get('kind')}' must define supported_sections as a string list",
                )
            )
            continue
        location = f"{source_repo}/{surface_file}"
        surface_path = source_root / surface_file
        try:
            payload = ensure_mapping(load_json_file(surface_path), location)
            entries = ensure_list(payload.get(section_array_key(hint["kind"])), location)
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
                        f"duplicate expand match '{match_value}' for kind '{hint['kind']}'",
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
                    content_markdown = section.get("content_markdown")
                    if not isinstance(heading, str) or not heading.strip():
                        raise RouterError(f"{section_location}.heading must be a non-empty string")
                    if not isinstance(content_markdown, str) or not content_markdown.strip():
                        raise RouterError(
                            f"{section_location}.content_markdown must be a non-empty string"
                        )
                except RouterError as exc:
                    issues.append(ValidationIssue(location, str(exc)))
                    continue
                section_keys.append(section_key)

            if len(section_keys) != len(set(section_keys)):
                issues.append(
                    ValidationIssue(
                        location,
                        f"expand surface contains duplicate section keys for {hint['kind']} match '{match_value}'",
                    )
                )
            section_keys_by_match[match_value] = section_keys

        expected_matches = {
            entry["id"] if match_field == "id" else entry["name"]
            for entry in registry_entries
            if entry["kind"] == hint["kind"]
        }
        missing_matches = sorted(expected_matches - seen_matches)
        for match_value in missing_matches:
            issues.append(
                ValidationIssue(
                    location,
                    f"expand surface is missing {hint['kind']} match '{match_value}'",
                )
            )
        unexpected_matches = sorted(seen_matches - expected_matches)
        for match_value in unexpected_matches:
            issues.append(
                ValidationIssue(
                    location,
                    f"expand surface contains unexpected {hint['kind']} match '{match_value}'",
                )
            )

        if any(section not in supported_sections for section in default_sections):
            issues.append(
                ValidationIssue(
                    "task_to_surface_hints.json",
                    f"default expand sections for kind '{hint['kind']}' must be a subset of supported_sections",
                )
            )

        supported_tuple = tuple(supported_sections)
        default_tuple = tuple(default_sections)
        for match_value in sorted(expected_matches & seen_matches):
            actual_keys = tuple(section_keys_by_match.get(match_value, []))
            if actual_keys != supported_tuple:
                issues.append(
                    ValidationIssue(
                        location,
                        f"expand surface for {hint['kind']} match '{match_value}' must expose the supported section order",
                    )
                )
                continue
            missing_defaults = [section for section in default_tuple if section not in actual_keys]
            if missing_defaults:
                issues.append(
                    ValidationIssue(
                        location,
                        f"expand surface for {hint['kind']} match '{match_value}' is missing default sections: {', '.join(missing_defaults)}",
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


def validate_generated_outputs(
    generated_dir: Path,
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    generated_dir = generated_dir.resolve()

    registry_path = generated_dir / "cross_repo_registry.min.json"
    router_path = generated_dir / "aoa_router.min.json"
    hints_path = generated_dir / "task_to_surface_hints.json"
    recommended_path = generated_dir / "recommended_paths.min.json"

    registry_payload = load_output(registry_path, issues)
    router_payload = load_output(router_path, issues)
    hints_payload = load_output(hints_path, issues)
    recommended_payload = load_output(recommended_path, issues)
    if any(payload is None for payload in (registry_payload, router_payload, hints_payload, recommended_payload)):
        return issues

    for output_path, payload in (
        (registry_path, registry_payload),
        (router_path, router_payload),
        (hints_path, hints_payload),
        (recommended_path, recommended_payload),
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
        if entry.get("kind") == "memo":
            issues.append(ValidationIssue(location, "memo entries are not allowed in v0.1"))
        if entry.get("repo") == "aoa-memo":
            issues.append(ValidationIssue(location, "aoa-memo repo entries are not allowed in v0.1"))
        if entry.get("kind") in ACTIVE_KINDS and entry.get("source_type") != "generated-catalog":
            issues.append(
                ValidationIssue(
                    location,
                    "active registry entries must use source_type 'generated-catalog'",
                )
            )
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
        if entry.get("kind") == "memo":
            issues.append(ValidationIssue(location, "memo router entries are not allowed in v0.1"))
        if "source_type" in entry or "attributes" in entry:
            issues.append(ValidationIssue(location, "router entries must stay as the thin projection surface"))
        normalized_router_entries.append(entry)

    if router_payload != build_router_payload(projection_safe_registry_entries):
        issues.append(ValidationIssue(router_path.name, "aoa_router.min.json does not match the registry projection"))

    if hints_payload != build_task_to_surface_hints_payload():
        issues.append(ValidationIssue(hints_path.name, "task_to_surface_hints.json does not match the expected static dispatch surface"))
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
        if entry.get("kind") == "memo":
            issues.append(ValidationIssue(location, "memo recommended path entries are not allowed in v0.1"))
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
                if raw_hop.get("kind") not in ACTIVE_KINDS:
                    issues.append(ValidationIssue(hop_location, "hop kind must be technique, skill, or eval"))
                if raw_hop.get("kind") == entry.get("kind"):
                    issues.append(ValidationIssue(hop_location, "same-kind hops are not allowed in v0.1"))
                if raw_hop.get("kind") == "memo":
                    issues.append(ValidationIssue(hop_location, "memo hops are not allowed in v0.1"))

    try:
        expected_recommended = build_recommended_paths_payload(recommended_safe_registry_entries)
    except RouterError as exc:
        issues.append(ValidationIssue(recommended_path.name, str(exc)))
    else:
        if recommended_payload != expected_recommended:
            issues.append(ValidationIssue(recommended_path.name, "recommended_paths.min.json does not match registry-derived dependencies"))

    for filename, payload in (
        (registry_path.name, registry_payload),
        (router_path.name, router_payload),
        (hints_path.name, hints_payload),
        (recommended_path.name, recommended_payload),
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
    )
    if issues:
        for issue in issues:
            print(f"[error] {issue.location}: {issue.message}")
        return 1
    print("[ok] validated generated routing outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
