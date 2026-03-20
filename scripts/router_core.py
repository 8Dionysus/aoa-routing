#!/usr/bin/env python3
"""Shared helpers for aoa-routing build and validation flows."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_KINDS = ("technique", "skill", "eval")
RESERVED_KINDS = ("memo",)
ALL_KINDS = ACTIVE_KINDS + RESERVED_KINDS
KNOWN_REPOS = (
    "aoa-routing",
    "aoa-techniques",
    "aoa-skills",
    "aoa-evals",
    "aoa-memo",
)
KIND_ORDER = {kind: index for index, kind in enumerate(ALL_KINDS)}
RELATION_REQUIRES = "requires"
RELATION_REQUIRED_BY = "required_by"
PENDING_TECHNIQUE_PREFIX = "AOA-T-PENDING-"


class RouterError(RuntimeError):
    """Raised when build or validation inputs are inconsistent."""


def relative_posix(path: Path, root: Path | None = None) -> str:
    target_root = root or REPO_ROOT
    try:
        return path.relative_to(target_root).as_posix()
    except ValueError:
        return path.as_posix()


def load_json_file(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise RouterError(f"{relative_posix(path)} is missing") from exc
    except json.JSONDecodeError as exc:
        raise RouterError(f"{relative_posix(path)} is invalid JSON: {exc}") from exc


def load_yaml_file(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise RouterError(f"{relative_posix(path)} is missing") from exc
    except yaml.YAMLError as exc:
        raise RouterError(f"{relative_posix(path)} is invalid YAML: {exc}") from exc


def parse_frontmatter_markdown(path: Path) -> tuple[dict[str, Any], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RouterError(f"{relative_posix(path)} is missing") from exc

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise RouterError(
            f"{relative_posix(path)} is missing YAML frontmatter opening delimiter"
        )

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        raise RouterError(
            f"{relative_posix(path)} is missing YAML frontmatter closing delimiter"
        )

    frontmatter_text = "\n".join(lines[1:closing_index])
    body = "\n".join(lines[closing_index + 1 :])

    try:
        metadata = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as exc:
        raise RouterError(f"{relative_posix(path)} has invalid frontmatter YAML: {exc}") from exc

    if not isinstance(metadata, dict):
        raise RouterError(f"{relative_posix(path)} frontmatter must parse to a mapping")
    return metadata, body


def write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(
        payload,
        ensure_ascii=False,
        indent=None,
        separators=(",", ":"),
        sort_keys=False,
    )
    path.write_text(f"{text}\n", encoding="utf-8")


def ensure_mapping(data: Any, location: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise RouterError(f"{location} must be a mapping")
    return data


def ensure_list(data: Any, location: str) -> list[Any]:
    if not isinstance(data, list):
        raise RouterError(f"{location} must be a list")
    return data


def ensure_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RouterError(f"{location} must be a non-empty string")
    return value


def ensure_bool(value: Any, location: str) -> bool:
    if not isinstance(value, bool):
        raise RouterError(f"{location} must be a boolean")
    return value


def ensure_int(value: Any, location: str) -> int:
    if not isinstance(value, int):
        raise RouterError(f"{location} must be an integer")
    return value


def ensure_string_list(values: Any, location: str) -> list[str]:
    items = ensure_list(values, location)
    result: list[str] = []
    for index, item in enumerate(items):
        result.append(ensure_string(item, f"{location}[{index}]"))
    return result


def require_keys(data: dict[str, Any], keys: Iterable[str], location: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise RouterError(f"{location} is missing required keys: {', '.join(missing)}")


def normalize_repo_name(raw: str) -> str:
    text = raw.strip()
    if not text:
        raise RouterError("repo value must not be empty")
    if text in KNOWN_REPOS:
        return text

    if text.startswith("git@"):
        text = text.split(":", 1)[-1]
    if "://" in text:
        text = text.split("://", 1)[-1]
        if "/" in text:
            text = text.split("/", 1)[-1]
    text = text.rstrip("/")
    if text.endswith(".git"):
        text = text[:-4]

    candidate = text.rsplit("/", 1)[-1]
    if candidate in KNOWN_REPOS:
        return candidate

    raise RouterError(f"unsupported repo reference '{raw}'")


def ensure_repo_relative_path(raw_path: str, location: str) -> str:
    value = ensure_string(raw_path, location)
    if re.match(r"^[A-Za-z]:[/\\\\]", value) or value.startswith(("/", "\\\\")):
        raise RouterError(f"{location} must be repo-relative, not absolute")
    return value.replace("\\", "/")


def is_pending_technique_id(identifier: str) -> bool:
    return identifier.startswith(PENDING_TECHNIQUE_PREFIX)


def sort_registry_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(entries, key=lambda entry: (KIND_ORDER[entry["kind"]], entry["id"]))


def sort_hops(hops: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(hops, key=lambda hop: (KIND_ORDER[hop["kind"]], hop["id"], hop["relation"]))


def build_router_payload(registry_entries: list[dict[str, Any]]) -> dict[str, Any]:
    projection = [
        {
            "kind": entry["kind"],
            "id": entry["id"],
            "name": entry["name"],
            "repo": entry["repo"],
            "path": entry["path"],
            "status": entry["status"],
            "summary": entry["summary"],
        }
        for entry in sort_registry_entries(list(registry_entries))
        if entry["kind"] != "memo"
    ]
    return {
        "router_version": 1,
        "entries": projection,
    }


def build_task_to_surface_hints_payload() -> dict[str, Any]:
    def action_flags(
        *,
        inspect_enabled: bool,
        surface_file: str | None = None,
        match_field: str | None = None,
        pick_enabled: bool = True,
    ) -> dict[str, dict[str, Any]]:
        inspect: dict[str, Any] = {"enabled": inspect_enabled}
        if inspect_enabled:
            inspect["surface_file"] = surface_file
            inspect["match_field"] = match_field
        return {
            "pick": {"enabled": pick_enabled},
            "inspect": inspect,
            "expand": {"enabled": False},
            "pair": {"enabled": False},
            "recall": {"enabled": False},
        }

    return {
        "version": 1,
        "hints": [
            {
                "kind": "technique",
                "enabled": True,
                "source_repo": "aoa-techniques",
                "use_when": "need a reusable engineering practice or minimal technique selection",
                "actions": action_flags(
                    inspect_enabled=True,
                    surface_file="generated/technique_capsules.json",
                    match_field="id",
                ),
            },
            {
                "kind": "skill",
                "enabled": True,
                "source_repo": "aoa-skills",
                "use_when": "need a bounded agent-facing workflow to execute",
                "actions": action_flags(
                    inspect_enabled=True,
                    surface_file="generated/skill_capsules.json",
                    match_field="name",
                ),
            },
            {
                "kind": "eval",
                "enabled": True,
                "source_repo": "aoa-evals",
                "use_when": "need a bounded proof or quality-check surface",
                "actions": action_flags(
                    inspect_enabled=True,
                    surface_file="generated/eval_capsules.json",
                    match_field="name",
                ),
            },
            {
                "kind": "memo",
                "enabled": False,
                "source_repo": "aoa-memo",
                "use_when": "reserved for future recall and memory-routing surfaces",
                "actions": action_flags(inspect_enabled=False, pick_enabled=False),
            },
        ],
    }


def build_recommended_paths_payload(registry_entries: list[dict[str, Any]]) -> dict[str, Any]:
    index = {(entry["kind"], entry["id"]): entry for entry in registry_entries}
    adjacency: dict[tuple[str, str], dict[str, list[dict[str, str]]]] = {
        (entry["kind"], entry["id"]): {"upstream": [], "downstream": []}
        for entry in registry_entries
        if entry["kind"] != "memo"
    }

    def add_hop(
        source_key: tuple[str, str],
        target_kind: str,
        target_id: str,
    ) -> None:
        if target_kind == "memo":
            raise RouterError("memo hops are not supported in v0.1")
        if target_kind == source_key[0]:
            raise RouterError(
                f"same-kind hop is not allowed for {source_key[0]}:{source_key[1]} -> {target_id}"
            )
        if target_kind == "technique" and is_pending_technique_id(target_id):
            return
        target_key = (target_kind, target_id)
        if target_key not in index:
            raise RouterError(
                f"unresolved dependency: {source_key[0]}:{source_key[1]} -> {target_kind}:{target_id}"
            )
        adjacency[source_key]["upstream"].append(
            {"kind": target_kind, "id": target_id, "relation": RELATION_REQUIRES}
        )
        adjacency[target_key]["downstream"].append(
            {"kind": source_key[0], "id": source_key[1], "relation": RELATION_REQUIRED_BY}
        )

    for entry in registry_entries:
        if entry["kind"] == "skill":
            for dependency_id in entry["attributes"]["technique_dependencies"]:
                add_hop((entry["kind"], entry["id"]), "technique", dependency_id)
        elif entry["kind"] == "eval":
            for dependency_id in entry["attributes"]["technique_dependencies"]:
                add_hop((entry["kind"], entry["id"]), "technique", dependency_id)
            for dependency_name in entry["attributes"]["skill_dependencies"]:
                add_hop((entry["kind"], entry["id"]), "skill", dependency_name)

    payload_entries = []
    for entry in sort_registry_entries(list(registry_entries)):
        if entry["kind"] == "memo":
            continue
        key = (entry["kind"], entry["id"])
        payload_entries.append(
            {
                "kind": entry["kind"],
                "id": entry["id"],
                "upstream": sort_hops(adjacency[key]["upstream"]),
                "downstream": sort_hops(adjacency[key]["downstream"]),
            }
        )
    return {
        "version": 1,
        "entries": payload_entries,
    }
