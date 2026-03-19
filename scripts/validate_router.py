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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate aoa-routing generated outputs.")
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
def get_schema_validator(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(schema_name))


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
) -> None:
    attributes = entry.get("attributes")
    if not isinstance(attributes, dict):
        issues.append(ValidationIssue(location, "attributes must be an object"))
        return

    kind = entry["kind"]
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
            return
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
        return

    if kind == "skill":
        expected_keys = {"scope", "invocation_mode", "technique_dependencies"}
        if set(attributes) != expected_keys:
            issues.append(ValidationIssue(location, "skill attributes do not match the expected shape"))
            return
        for key in ("scope", "invocation_mode"):
            if not isinstance(attributes[key], str):
                issues.append(ValidationIssue(location, f"skill {key} must be a string"))
        try:
            ensure_string_list(attributes["technique_dependencies"], f"{location}.technique_dependencies")
        except RouterError as exc:
            issues.append(ValidationIssue(location, str(exc)))
        return

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
            return
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
        return

    issues.append(ValidationIssue(location, f"unsupported entry kind '{kind}'"))


def validate_registry_dependencies(
    registry_entries: list[dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    entries_by_kind: dict[str, set[str]] = {kind: set() for kind in ACTIVE_KINDS}
    for entry in registry_entries:
        entries_by_kind.setdefault(entry["kind"], set()).add(entry["id"])

    for entry in registry_entries:
        location = f"cross_repo_registry.min.json:{entry['kind']}:{entry['id']}"
        if entry["kind"] == "skill":
            for dependency_id in entry["attributes"]["technique_dependencies"]:
                if is_pending_technique_id(dependency_id):
                    continue
                if dependency_id not in entries_by_kind["technique"]:
                    issues.append(
                        ValidationIssue(location, f"unresolved technique dependency '{dependency_id}'")
                    )
        elif entry["kind"] == "eval":
            for dependency_id in entry["attributes"]["technique_dependencies"]:
                if is_pending_technique_id(dependency_id):
                    continue
                if dependency_id not in entries_by_kind["technique"]:
                    issues.append(
                        ValidationIssue(location, f"unresolved technique dependency '{dependency_id}'")
                    )
            for dependency_name in entry["attributes"]["skill_dependencies"]:
                if dependency_name not in entries_by_kind["skill"]:
                    issues.append(
                        ValidationIssue(location, f"unresolved skill dependency '{dependency_name}'")
                    )


def validate_generated_outputs(generated_dir: Path) -> list[ValidationIssue]:
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

    if registry_payload.get("registry_version") != 1:
        issues.append(ValidationIssue(registry_path.name, "registry_version must be 1"))
    if registry_payload.get("reserved_kinds") != list(RESERVED_KINDS):
        issues.append(ValidationIssue(registry_path.name, "reserved_kinds must equal ['memo']"))
    try:
        registry_entries = ensure_list(registry_payload.get("entries"), f"{registry_path.name}.entries")
    except RouterError as exc:
        issues.append(ValidationIssue(registry_path.name, str(exc)))
        return issues

    normalized_registry_entries: list[dict[str, Any]] = []
    seen_registry_keys: set[tuple[str, str]] = set()
    for index, raw_entry in enumerate(registry_entries):
        location = f"{registry_path.name}.entries[{index}]"
        try:
            entry = ensure_mapping(raw_entry, location)
        except RouterError as exc:
            issues.append(ValidationIssue(registry_path.name, str(exc)))
            continue
        validate_against_schema(entry, "router-entry.schema.json", location, issues)
        key = (entry.get("kind"), entry.get("id"))
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
        validate_registry_entry_attributes(entry, location, issues)
        normalized_registry_entries.append(entry)

    validate_registry_dependencies(normalized_registry_entries, issues)

    if router_payload.get("router_version") != 1:
        issues.append(ValidationIssue(router_path.name, "router_version must be 1"))
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
        key = (entry.get("kind"), entry.get("id"))
        if key in seen_router_keys:
            issues.append(ValidationIssue(location, f"duplicate router entry for {key[0]}:{key[1]}"))
        else:
            seen_router_keys.add(key)
        if entry.get("kind") == "memo":
            issues.append(ValidationIssue(location, "memo router entries are not allowed in v0.1"))
        if "source_type" in entry or "attributes" in entry:
            issues.append(ValidationIssue(location, "router entries must stay as the thin projection surface"))
        normalized_router_entries.append(entry)

    if router_payload != build_router_payload(normalized_registry_entries):
        issues.append(ValidationIssue(router_path.name, "aoa_router.min.json does not match the registry projection"))

    if hints_payload != build_task_to_surface_hints_payload():
        issues.append(ValidationIssue(hints_path.name, "task_to_surface_hints.json does not match the expected static dispatch surface"))

    if recommended_payload.get("version") != 1:
        issues.append(ValidationIssue(recommended_path.name, "version must be 1"))
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
        expected_recommended = build_recommended_paths_payload(normalized_registry_entries)
    except RouterError as exc:
        issues.append(ValidationIssue(recommended_path.name, str(exc)))
    else:
        if recommended_payload != expected_recommended:
            issues.append(ValidationIssue(recommended_path.name, "recommended_paths.min.json does not match registry-derived dependencies"))

    return issues


def main() -> int:
    args = parse_args()
    issues = validate_generated_outputs(args.generated_dir)
    if issues:
        for issue in issues:
            print(f"[error] {issue.location}: {issue.message}")
        return 1
    print("[ok] validated generated routing outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
