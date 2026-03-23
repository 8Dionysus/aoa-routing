#!/usr/bin/env python3
"""Shared helpers for aoa-routing build and validation flows."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_KINDS = ("technique", "skill", "eval", "memo")
RESERVED_KINDS: tuple[str, ...] = ()
ALL_KINDS = ACTIVE_KINDS + RESERVED_KINDS
PAIRABLE_KINDS = ("technique", "skill", "eval")
RECOMMENDED_HOP_KINDS = ("technique", "skill", "eval")
CANONICAL_REPO_BY_KIND = {
    "technique": "aoa-techniques",
    "skill": "aoa-skills",
    "eval": "aoa-evals",
    "memo": "aoa-memo",
}
KNOWN_REPOS = ("aoa-routing",) + tuple(CANONICAL_REPO_BY_KIND.values())
KIND_ORDER = {kind: index for index, kind in enumerate(ALL_KINDS)}
RELATION_REQUIRES = "requires"
RELATION_REQUIRED_BY = "required_by"
PENDING_TECHNIQUE_PREFIX = "AOA-T-PENDING-"
KAG_SOURCE_LIFT_TECHNIQUE_IDS = (
    "AOA-T-0018",
    "AOA-T-0019",
    "AOA-T-0020",
    "AOA-T-0021",
    "AOA-T-0022",
)
KAG_SOURCE_LIFT_TECHNIQUE_SET = set(KAG_SOURCE_LIFT_TECHNIQUE_IDS)
DIRECT_RELATION_TYPES = (
    "requires",
    "complements",
    "supersedes",
    "conflicts_with",
    "used_together_for",
    "derived_from",
    "shares_contract_with",
)
DIRECT_RELATION_TYPES_SET = set(DIRECT_RELATION_TYPES)
MODEL_TIER_SOURCE_REPO = "aoa-agents"
MODEL_TIER_REGISTRY_PATH = "generated/model_tier_registry.json"
PAIRING_SURFACE_REPO = "aoa-routing"
PAIRING_SURFACE_FILE = "generated/pairing_hints.min.json"
TINY_MODEL_ENTRYPOINTS_FILE = "generated/tiny_model_entrypoints.json"
DEFAULT_MEMO_RECALL_MODE = "semantic"
ROUTER_READY_RECALL_CONTRACT_PREFIX = "recall_contract.router."
KAG_DEFAULT_ENTRYPOINT_ID = "AOA-T-0019"
TASK_TO_TIER_HINT_SPECS = (
    {
        "task_family": "task-triage",
        "preferred_tier": "router",
        "fallback_tier": "planner",
        "use_when": "need the fastest classification of task shape, risk, and smallest next step",
    },
    {
        "task_family": "bounded-plan-shaping",
        "preferred_tier": "planner",
        "fallback_tier": "conductor",
        "use_when": "need an explicit bounded plan, checks, and escalation boundaries",
    },
    {
        "task_family": "bounded-execution",
        "preferred_tier": "executor",
        "fallback_tier": "planner",
        "use_when": "need the current bounded slice executed after the route and plan are already explicit",
    },
    {
        "task_family": "verification-pass",
        "preferred_tier": "verifier",
        "fallback_tier": "conductor",
        "use_when": "need contradiction checks, output review, or a named continue-stop-escalate decision",
    },
    {
        "task_family": "tier-transition-governance",
        "preferred_tier": "conductor",
        "fallback_tier": "verifier",
        "use_when": "need a route-level decision about continue, pause, escalate, or distill",
    },
    {
        "task_family": "high-cost-synthesis",
        "preferred_tier": "deep",
        "fallback_tier": "conductor",
        "use_when": "need rare deep synthesis, contradiction arbitration, or high-cost final judgment",
    },
    {
        "task_family": "distillation-and-writeback-prep",
        "preferred_tier": "archivist",
        "fallback_tier": "conductor",
        "use_when": "need summaries, decisions, and memory candidates distilled after a non-trivial run",
    },
)


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
    normalized = value.replace("\\", "/")
    if ".." in Path(normalized).parts:
        raise RouterError(f"{location} must not traverse outside the repository root")
    return normalized


def is_pending_technique_id(identifier: str) -> bool:
    return identifier.startswith(PENDING_TECHNIQUE_PREFIX)


def sort_registry_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(entries, key=lambda entry: (KIND_ORDER[entry["kind"]], entry["id"]))


def sort_hops(hops: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(hops, key=lambda hop: (KIND_ORDER[hop["kind"]], hop["id"], hop["relation"]))


def load_technique_catalog_entries(techniques_root: Path) -> tuple[str, list[dict[str, Any]]]:
    for filename in ("technique_catalog.json", "technique_catalog.min.json"):
        catalog_path = techniques_root / "generated" / filename
        if not catalog_path.exists():
            continue
        payload = ensure_mapping(load_json_file(catalog_path), relative_posix(catalog_path))
        return catalog_path.relative_to(techniques_root).as_posix(), ensure_list(
            payload.get("techniques"),
            f"{relative_posix(catalog_path)}.techniques",
        )
    raise RouterError(
        f"{relative_posix(techniques_root / 'generated' / 'technique_catalog.json')} is missing"
    )


def load_model_tier_registry(
    agents_root: Path,
    registry_relative_path: str = MODEL_TIER_REGISTRY_PATH,
) -> tuple[str, dict[str, dict[str, str]]]:
    normalized_path = ensure_repo_relative_path(registry_relative_path, "tier_registry_path")
    registry_path = agents_root / normalized_path
    location = relative_posix(registry_path, agents_root)
    payload = ensure_mapping(load_json_file(registry_path), location)
    model_tiers = ensure_list(payload.get("model_tiers"), f"{location}.model_tiers")

    tier_index: dict[str, dict[str, str]] = {}
    for index, item in enumerate(model_tiers):
        tier_location = f"{location}.model_tiers[{index}]"
        tier = ensure_mapping(item, tier_location)
        require_keys(tier, ("id", "artifact_requirement"), tier_location)
        tier_id = ensure_string(tier["id"], f"{tier_location}.id")
        if tier_id in tier_index:
            raise RouterError(f"{tier_location}.id duplicates tier '{tier_id}'")
        tier_index[tier_id] = {
            "artifact_requirement": ensure_string(
                tier["artifact_requirement"],
                f"{tier_location}.artifact_requirement",
            )
        }
    return normalized_path, tier_index


def load_memo_catalog_surfaces(memo_root: Path) -> list[dict[str, Any]]:
    catalog_path = memo_root / "generated" / "memory_catalog.min.json"
    payload = ensure_mapping(load_json_file(catalog_path), relative_posix(catalog_path))
    raw_surfaces = ensure_list(
        payload.get("memo_surfaces"),
        f"{relative_posix(catalog_path)}.memo_surfaces",
    )
    surfaces: list[dict[str, Any]] = []
    for index, item in enumerate(raw_surfaces):
        location = f"{relative_posix(catalog_path)}.memo_surfaces[{index}]"
        surfaces.append(ensure_mapping(item, location))
    return surfaces


def collect_memo_recall_mode_order(memo_surfaces: list[dict[str, Any]]) -> list[str]:
    ordered_modes: list[str] = []
    seen_modes: set[str] = set()
    for index, surface in enumerate(memo_surfaces):
        location = f"generated/memory_catalog.min.json.memo_surfaces[{index}]"
        modes = ensure_string_list(surface.get("recall_modes"), f"{location}.recall_modes")
        for mode in modes:
            if mode in seen_modes:
                continue
            ordered_modes.append(mode)
            seen_modes.add(mode)
    return ordered_modes


def load_router_ready_memo_recall_contracts(
    memo_root: Path,
    memo_surfaces: list[dict[str, Any]] | None = None,
) -> tuple[str | None, list[str], dict[str, str]]:
    surfaces = memo_surfaces or load_memo_catalog_surfaces(memo_root)
    declared_modes = collect_memo_recall_mode_order(surfaces)
    declared_mode_set = set(declared_modes)
    contracts_by_mode: dict[str, str] = {}

    examples_dir = memo_root / "examples"
    if examples_dir.exists():
        for contract_path in sorted(examples_dir.glob(f"{ROUTER_READY_RECALL_CONTRACT_PREFIX}*.json")):
            location = relative_posix(contract_path, memo_root)
            contract = ensure_mapping(load_json_file(contract_path), location)
            require_keys(
                contract,
                ("mode", "inspect_surface", "expand_surface"),
                location,
            )
            mode = ensure_string(contract["mode"], f"{location}.mode")
            if mode in contracts_by_mode:
                raise RouterError(f"{location} duplicates router-ready recall mode '{mode}'")
            if mode not in declared_mode_set:
                raise RouterError(
                    f"{location}.mode must be declared by aoa-memo/generated/memory_catalog.min.json"
                )
            contracts_by_mode[mode] = location

    supported_modes = [mode for mode in declared_modes if mode in contracts_by_mode]
    if not supported_modes:
        return None, [], {}

    default_mode = DEFAULT_MEMO_RECALL_MODE if DEFAULT_MEMO_RECALL_MODE in contracts_by_mode else supported_modes[0]
    return default_mode, supported_modes, contracts_by_mode


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
    ]
    return {
        "router_version": 1,
        "entries": projection,
    }


def build_task_to_surface_hints_payload(memo_root: Path) -> dict[str, Any]:
    def action_flags(
        *,
        inspect_enabled: bool,
        surface_file: str | None = None,
        match_field: str | None = None,
        expand_enabled: bool = False,
        expand_surface_file: str | None = None,
        expand_match_field: str | None = None,
        expand_section_key_field: str = "key",
        default_sections: list[str] | None = None,
        supported_sections: list[str] | None = None,
        pick_enabled: bool = True,
        pair_enabled: bool = False,
        pair_surface_repo: str | None = None,
        pair_surface_file: str | None = None,
        pair_match_field: str | None = None,
        recall_enabled: bool = False,
        recall_contract_file: str | None = None,
        recall_default_mode: str | None = None,
        recall_supported_modes: list[str] | None = None,
        recall_contracts_by_mode: dict[str, str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        inspect: dict[str, Any] = {"enabled": inspect_enabled}
        if inspect_enabled:
            inspect["surface_file"] = surface_file
            inspect["match_field"] = match_field
        expand: dict[str, Any] = {"enabled": expand_enabled}
        if expand_enabled:
            expand["surface_file"] = expand_surface_file
            expand["match_field"] = expand_match_field
            expand["section_key_field"] = expand_section_key_field
            expand["default_sections"] = list(default_sections or [])
            expand["supported_sections"] = list(supported_sections or [])
        pair: dict[str, Any] = {"enabled": pair_enabled}
        if pair_enabled:
            pair["surface_repo"] = pair_surface_repo
            pair["surface_file"] = pair_surface_file
            pair["match_field"] = pair_match_field
        recall: dict[str, Any] = {"enabled": recall_enabled}
        if recall_enabled:
            if recall_contract_file is not None:
                recall["contract_file"] = recall_contract_file
            recall["default_mode"] = recall_default_mode
            recall["supported_modes"] = list(recall_supported_modes or [])
            recall["contracts_by_mode"] = dict(recall_contracts_by_mode or {})
        return {
            "pick": {"enabled": pick_enabled},
            "inspect": inspect,
            "expand": expand,
            "pair": pair,
            "recall": recall,
        }

    memo_surfaces = load_memo_catalog_surfaces(memo_root)
    recall_default_mode, recall_supported_modes, recall_contracts_by_mode = (
        load_router_ready_memo_recall_contracts(memo_root, memo_surfaces)
    )
    recall_contract_file = None
    if recall_default_mode is not None:
        recall_contract_file = recall_contracts_by_mode[recall_default_mode]

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
                    expand_enabled=True,
                    expand_surface_file="generated/technique_sections.full.json",
                    expand_match_field="id",
                    default_sections=[
                        "intent",
                        "when_to_use",
                        "inputs",
                        "outputs",
                        "core_procedure",
                        "contracts",
                        "risks",
                        "validation",
                    ],
                    supported_sections=[
                        "intent",
                        "when_to_use",
                        "when_not_to_use",
                        "inputs",
                        "outputs",
                        "core_procedure",
                        "contracts",
                        "risks",
                        "validation",
                        "adaptation_notes",
                        "public_sanitization_notes",
                        "example",
                        "checks",
                        "promotion_history",
                        "future_evolution",
                    ],
                    pair_enabled=True,
                    pair_surface_repo=PAIRING_SURFACE_REPO,
                    pair_surface_file=PAIRING_SURFACE_FILE,
                    pair_match_field="id",
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
                    expand_enabled=True,
                    expand_surface_file="generated/skill_sections.full.json",
                    expand_match_field="name",
                    default_sections=[
                        "intent",
                        "trigger_boundary",
                        "inputs",
                        "outputs",
                        "procedure",
                        "contracts",
                        "risks_and_anti_patterns",
                        "verification",
                    ],
                    supported_sections=[
                        "intent",
                        "trigger_boundary",
                        "inputs",
                        "outputs",
                        "procedure",
                        "contracts",
                        "risks_and_anti_patterns",
                        "verification",
                        "technique_traceability",
                        "adaptation_points",
                    ],
                    pair_enabled=True,
                    pair_surface_repo=PAIRING_SURFACE_REPO,
                    pair_surface_file=PAIRING_SURFACE_FILE,
                    pair_match_field="id",
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
                    expand_enabled=True,
                    expand_surface_file="generated/eval_sections.full.json",
                    expand_match_field="name",
                    default_sections=[
                        "bounded_claim",
                        "trigger_boundary",
                        "inputs",
                        "scoring_or_verdict_logic",
                        "outputs",
                        "blind_spots",
                        "interpretation_guidance",
                        "verification",
                    ],
                    supported_sections=[
                        "intent",
                        "object_under_evaluation",
                        "bounded_claim",
                        "trigger_boundary",
                        "inputs",
                        "fixtures_and_case_surface",
                        "scoring_or_verdict_logic",
                        "baseline_or_comparison_mode",
                        "execution_contract",
                        "outputs",
                        "failure_modes",
                        "blind_spots",
                        "interpretation_guidance",
                        "verification",
                        "technique_traceability",
                        "skill_traceability",
                        "adaptation_points",
                    ],
                    pair_enabled=True,
                    pair_surface_repo=PAIRING_SURFACE_REPO,
                    pair_surface_file=PAIRING_SURFACE_FILE,
                    pair_match_field="id",
                ),
            },
            {
                "kind": "memo",
                "enabled": True,
                "source_repo": "aoa-memo",
                "use_when": "need bounded recall or memory-layer doctrine surfaces without copying memo truth into routing",
                "actions": action_flags(
                    inspect_enabled=True,
                    surface_file="generated/memory_catalog.min.json",
                    match_field="id",
                    expand_enabled=True,
                    expand_surface_file="generated/memory_sections.full.json",
                    expand_match_field="id",
                    expand_section_key_field="section_id",
                    default_sections=[],
                    supported_sections=[],
                    recall_enabled=bool(recall_supported_modes),
                    recall_contract_file=recall_contract_file,
                    recall_default_mode=recall_default_mode,
                    recall_supported_modes=recall_supported_modes,
                    recall_contracts_by_mode=recall_contracts_by_mode,
                ),
            },
        ],
    }


def build_pairing_hints_payload(
    registry_entries: list[dict[str, Any]],
    source_catalog: str,
    technique_catalog_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    index = {(entry["kind"], entry["id"]): entry for entry in registry_entries}
    pairings: dict[tuple[str, str], list[dict[str, str]]] = {
        (entry["kind"], entry["id"]): []
        for entry in registry_entries
        if entry["kind"] in PAIRABLE_KINDS
    }
    seen_pairs: dict[tuple[str, str], set[tuple[str, str, str]]] = {
        key: set() for key in pairings
    }

    def add_pair(source_key: tuple[str, str], target_kind: str, target_id: str, relation: str) -> None:
        if source_key[0] not in PAIRABLE_KINDS:
            return
        if target_kind == "memo":
            raise RouterError("memo entries must not appear in bounded pairing hints")
        if target_kind not in PAIRABLE_KINDS:
            raise RouterError(f"{target_kind} is not supported in the bounded pairing surface")
        if target_kind == "technique" and is_pending_technique_id(target_id):
            return
        if target_kind == source_key[0]:
            if source_key[0] != "technique":
                raise RouterError(
                    f"same-kind pairing is not allowed for {source_key[0]}:{source_key[1]} -> {target_id}"
                )
            if source_key[1] not in KAG_SOURCE_LIFT_TECHNIQUE_SET or target_id not in KAG_SOURCE_LIFT_TECHNIQUE_SET:
                raise RouterError(
                    f"same-kind pairing must stay within the KAG/source-lift family: {source_key[1]} -> {target_id}"
                )
            if relation not in DIRECT_RELATION_TYPES_SET:
                raise RouterError(
                    f"same-kind pairing for {source_key[1]} -> {target_id} must use a supported direct relation"
                )
        elif relation not in {RELATION_REQUIRES, RELATION_REQUIRED_BY}:
            raise RouterError(
                f"cross-kind pairing for {source_key[0]}:{source_key[1]} -> {target_kind}:{target_id} must use requires/required_by"
            )
        if (target_kind, target_id) not in index:
            raise RouterError(
                f"unresolved pairing target: {source_key[0]}:{source_key[1]} -> {target_kind}:{target_id}"
            )
        pair_key = (target_kind, target_id, relation)
        if pair_key in seen_pairs[source_key]:
            return
        seen_pairs[source_key].add(pair_key)
        pairings[source_key].append(
            {"kind": target_kind, "id": target_id, "relation": relation}
        )

    for entry in registry_entries:
        source_key = (entry["kind"], entry["id"])
        if entry["kind"] == "skill":
            for dependency_id in entry["attributes"]["technique_dependencies"]:
                add_pair(source_key, "technique", dependency_id, RELATION_REQUIRES)
                if ("technique", dependency_id) in pairings:
                    add_pair(("technique", dependency_id), "skill", entry["id"], RELATION_REQUIRED_BY)
        elif entry["kind"] == "eval":
            for dependency_id in entry["attributes"]["technique_dependencies"]:
                add_pair(source_key, "technique", dependency_id, RELATION_REQUIRES)
                if ("technique", dependency_id) in pairings:
                    add_pair(("technique", dependency_id), "eval", entry["id"], RELATION_REQUIRED_BY)
            for dependency_name in entry["attributes"]["skill_dependencies"]:
                add_pair(source_key, "skill", dependency_name, RELATION_REQUIRES)
                if ("skill", dependency_name) in pairings:
                    add_pair(("skill", dependency_name), "eval", entry["id"], RELATION_REQUIRED_BY)

    techniques_by_id: dict[str, dict[str, Any]] = {}
    for index_value, item in enumerate(technique_catalog_entries):
        location = f"generated/technique_catalog.min.json.techniques[{index_value}]"
        technique = ensure_mapping(item, location)
        require_keys(technique, ("id",), location)
        technique_id = ensure_string(technique["id"], f"{location}.id")
        techniques_by_id[technique_id] = technique

    for technique_id in KAG_SOURCE_LIFT_TECHNIQUE_IDS:
        technique = techniques_by_id.get(technique_id)
        if technique is None or ("technique", technique_id) not in pairings:
            continue
        raw_relations = technique.get("relations", [])
        if raw_relations is None:
            raw_relations = []
        relations = ensure_list(
            raw_relations,
            f"generated/technique_catalog.min.json.techniques[{technique_id}].relations",
        )
        for relation_index, raw_relation in enumerate(relations):
            relation_location = (
                f"generated/technique_catalog.min.json.techniques[{technique_id}].relations[{relation_index}]"
            )
            relation = ensure_mapping(raw_relation, relation_location)
            require_keys(relation, ("type", "target"), relation_location)
            relation_type = ensure_string(relation["type"], f"{relation_location}.type")
            target_id = ensure_string(relation["target"], f"{relation_location}.target")
            add_pair(("technique", technique_id), "technique", target_id, relation_type)

    payload_entries = []
    for entry in sort_registry_entries(list(registry_entries)):
        if entry["kind"] not in PAIRABLE_KINDS:
            continue
        key = (entry["kind"], entry["id"])
        payload_entries.append(
            {
                "kind": entry["kind"],
                "id": entry["id"],
                "pairs": sort_hops(pairings[key]),
            }
        )
    return {
        "version": 1,
        "source_inputs": {
            "registry_surface": "generated/cross_repo_registry.min.json",
            "kag_relation_source_repo": "aoa-techniques",
            "kag_relation_source_catalog": source_catalog,
        },
        "entries": payload_entries,
    }


def build_tiny_model_entrypoints_payload(
    registry_entries: list[dict[str, Any]],
    hints_payload: dict[str, Any],
) -> dict[str, Any]:
    registry_index = {(entry["kind"], entry["id"]): entry for entry in registry_entries}
    available_kinds = {entry["kind"] for entry in registry_entries}
    hints = ensure_list(hints_payload.get("hints"), "task_to_surface_hints.json.hints")
    memo_recall_supported_modes: list[str] = []
    queries: list[dict[str, Any]] = [
        {
            "verb": "pick",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": "generated/aoa_router.min.json",
            "match_key": "kind",
            "allowed_kinds": list(ACTIVE_KINDS),
        }
    ]

    for index, raw_hint in enumerate(hints):
        location = f"task_to_surface_hints.json.hints[{index}]"
        hint = ensure_mapping(raw_hint, location)
        kind = ensure_string(hint["kind"], f"{location}.kind")
        source_repo = ensure_string(hint["source_repo"], f"{location}.source_repo")
        actions = ensure_mapping(hint["actions"], f"{location}.actions")

        inspect = ensure_mapping(actions["inspect"], f"{location}.actions.inspect")
        if inspect.get("enabled") is True:
            queries.append(
                {
                    "verb": "inspect",
                    "source_repo": source_repo,
                    "target_surface": ensure_string(
                        inspect.get("surface_file"),
                        f"{location}.actions.inspect.surface_file",
                    ),
                    "match_key": ensure_string(
                        inspect.get("match_field"),
                        f"{location}.actions.inspect.match_field",
                    ),
                    "allowed_kinds": [kind],
                }
            )

        expand = ensure_mapping(actions["expand"], f"{location}.actions.expand")
        if expand.get("enabled") is True:
            queries.append(
                {
                    "verb": "expand",
                    "source_repo": source_repo,
                    "target_surface": ensure_string(
                        expand.get("surface_file"),
                        f"{location}.actions.expand.surface_file",
                    ),
                    "match_key": ensure_string(
                        expand.get("match_field"),
                        f"{location}.actions.expand.match_field",
                    ),
                    "allowed_kinds": [kind],
                    "section_key_field": ensure_string(
                        expand.get("section_key_field"),
                        f"{location}.actions.expand.section_key_field",
                    ),
                    "default_sections": ensure_string_list(
                        expand.get("default_sections"),
                        f"{location}.actions.expand.default_sections",
                    ),
                }
            )

        pair = ensure_mapping(actions["pair"], f"{location}.actions.pair")
        if pair.get("enabled") is True:
            queries.append(
                {
                    "verb": "pair",
                    "source_repo": ensure_string(
                        pair.get("surface_repo"),
                        f"{location}.actions.pair.surface_repo",
                    ),
                    "target_surface": ensure_string(
                        pair.get("surface_file"),
                        f"{location}.actions.pair.surface_file",
                    ),
                    "match_key": ensure_string(
                        pair.get("match_field"),
                        f"{location}.actions.pair.match_field",
                    ),
                    "allowed_kinds": [kind],
                }
            )

        recall = ensure_mapping(actions["recall"], f"{location}.actions.recall")
        if recall.get("enabled") is True:
            queries.append(
                {
                    "verb": "recall",
                    "source_repo": PAIRING_SURFACE_REPO,
                    "target_surface": "generated/task_to_surface_hints.json",
                    "match_key": "kind",
                    "allowed_kinds": [kind],
                }
            )
            if kind == "memo":
                memo_recall_supported_modes = ensure_string_list(
                    recall.get("supported_modes"),
                    f"{location}.actions.recall.supported_modes",
                )

    starters: list[dict[str, Any]] = [
        {
            "name": "router-root",
            "verb": "pick",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": "generated/aoa_router.min.json",
            "match_key": "kind",
            "allowed_kinds": list(ACTIVE_KINDS),
        }
    ]
    for kind in ACTIVE_KINDS:
        if kind not in available_kinds:
            continue
        starters.append(
            {
                "name": f"{kind}-root",
                "verb": "pick",
                "source_repo": PAIRING_SURFACE_REPO,
                "target_surface": "generated/aoa_router.min.json",
                "match_key": "kind",
                "allowed_kinds": [kind],
                "target_kind": kind,
                "target_value": kind,
            }
        )
    for mode in memo_recall_supported_modes:
        starters.append(
            {
                "name": f"memo-recall-{mode.replace('_', '-')}",
                "verb": "recall",
                "source_repo": PAIRING_SURFACE_REPO,
                "target_surface": "generated/task_to_surface_hints.json",
                "match_key": "kind",
                "allowed_kinds": ["memo"],
                "target_kind": "memo",
                "target_value": "memo",
                "recall_mode": mode,
            }
        )
    if ("technique", KAG_DEFAULT_ENTRYPOINT_ID) in registry_index:
        starters.append(
            {
                "name": "kag-source-lift-default",
                "verb": "inspect",
                "source_repo": "aoa-techniques",
                "target_surface": "generated/technique_capsules.json",
                "match_key": "id",
                "allowed_kinds": ["technique"],
                "target_kind": "technique",
                "target_value": KAG_DEFAULT_ENTRYPOINT_ID,
            }
        )
        starters.append(
            {
                "name": "kag-source-lift-companions",
                "verb": "pair",
                "source_repo": PAIRING_SURFACE_REPO,
                "target_surface": PAIRING_SURFACE_FILE,
                "match_key": "id",
                "allowed_kinds": ["technique"],
                "target_kind": "technique",
                "target_value": KAG_DEFAULT_ENTRYPOINT_ID,
            }
        )

    return {
        "version": 1,
        "queries": queries,
        "starters": starters,
    }


def build_task_to_tier_hints_payload(agents_root: Path) -> dict[str, Any]:
    registry_relative_path, tier_index = load_model_tier_registry(agents_root)
    hints: list[dict[str, Any]] = []
    for spec in TASK_TO_TIER_HINT_SPECS:
        preferred_tier = spec["preferred_tier"]
        preferred_entry = tier_index.get(preferred_tier)
        if preferred_entry is None:
            raise RouterError(
                f"task-to-tier hint spec references unknown preferred tier '{preferred_tier}'"
            )

        fallback_tier = spec["fallback_tier"]
        if fallback_tier is not None and fallback_tier not in tier_index:
            raise RouterError(
                f"task-to-tier hint spec references unknown fallback tier '{fallback_tier}'"
            )

        hints.append(
            {
                "task_family": spec["task_family"],
                "preferred_tier": preferred_tier,
                "fallback_tier": fallback_tier,
                "use_when": spec["use_when"],
                "output_artifact": preferred_entry["artifact_requirement"],
            }
        )

    return {
        "version": 1,
        "source_of_truth": {
            "tier_registry_repo": MODEL_TIER_SOURCE_REPO,
            "tier_registry_path": registry_relative_path,
        },
        "hints": hints,
    }


def build_recommended_paths_payload(registry_entries: list[dict[str, Any]]) -> dict[str, Any]:
    index = {(entry["kind"], entry["id"]): entry for entry in registry_entries}
    adjacency: dict[tuple[str, str], dict[str, list[dict[str, str]]]] = {
        (entry["kind"], entry["id"]): {"upstream": [], "downstream": []}
        for entry in registry_entries
    }

    def add_hop(
        source_key: tuple[str, str],
        target_kind: str,
        target_id: str,
    ) -> None:
        if target_kind == source_key[0]:
            raise RouterError(
                f"same-kind hop is not allowed for {source_key[0]}:{source_key[1]} -> {target_id}"
            )
        if target_kind not in RECOMMENDED_HOP_KINDS:
            raise RouterError(f"{target_kind} hops are not supported in the bounded recommended path surface")
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


def build_kag_source_lift_relation_hints_payload(
    registry_entries: list[dict[str, Any]],
    source_catalog: str,
    technique_catalog_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    registry_index: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in registry_entries:
        kind = entry.get("kind")
        identifier = entry.get("id")
        if not isinstance(kind, str) or not isinstance(identifier, str):
            continue
        registry_index[(kind, identifier)] = entry
    techniques_by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(technique_catalog_entries):
        location = f"generated/technique_catalog.min.json.techniques[{index}]"
        technique = ensure_mapping(item, location)
        require_keys(technique, ("id", "name", "summary"), location)
        technique_id = ensure_string(technique["id"], f"{location}.id")
        if technique_id in techniques_by_id:
            raise RouterError(f"duplicate technique catalog entry for {technique_id}")
        techniques_by_id[technique_id] = technique

    payload_entries: list[dict[str, Any]] = []
    for technique_id in KAG_SOURCE_LIFT_TECHNIQUE_IDS:
        technique = techniques_by_id.get(technique_id)
        if technique is None:
            continue

        registry_entry = registry_index.get(("technique", technique_id))
        if registry_entry is None:
            raise RouterError(f"missing registry entry for technique relation hints {technique_id}")

        raw_relations = technique.get("relations", [])
        if raw_relations is None:
            raw_relations = []
        relations = ensure_list(
            raw_relations,
            f"generated/technique_catalog.min.json.techniques[{technique_id}].relations",
        )
        direct_relations: list[dict[str, str]] = []
        seen_relations: set[tuple[str, str]] = set()
        for relation_index, raw_relation in enumerate(relations):
            relation_location = (
                f"generated/technique_catalog.min.json.techniques[{technique_id}].relations[{relation_index}]"
            )
            relation = ensure_mapping(raw_relation, relation_location)
            require_keys(relation, ("type", "target"), relation_location)
            relation_type = ensure_string(relation["type"], f"{relation_location}.type")
            target_id = ensure_string(relation["target"], f"{relation_location}.target")
            if relation_type not in DIRECT_RELATION_TYPES_SET:
                raise RouterError(f"{relation_location}.type must be a supported direct relation type")
            if target_id == technique_id:
                raise RouterError(f"{relation_location}.target must not point to the same technique")
            if target_id not in KAG_SOURCE_LIFT_TECHNIQUE_SET:
                raise RouterError(
                    f"{relation_location}.target must stay within the KAG/source-lift family"
                )
            if (relation_type, target_id) in seen_relations:
                raise RouterError(
                    f"{relation_location} duplicates a direct relation already seen for {technique_id}"
                )
            if ("technique", target_id) not in registry_index:
                raise RouterError(
                    f"unresolved direct relation target: technique:{technique_id} -> technique:{target_id}"
                )
            seen_relations.add((relation_type, target_id))
            direct_relations.append({"type": relation_type, "target": target_id})

        payload_entries.append(
            {
                "kind": "technique",
                "id": registry_entry["id"],
                "name": registry_entry["name"],
                "summary": registry_entry["summary"],
                "relations": direct_relations,
            }
        )

    return {
        "version": 1,
        "scope": "kag_source_lift_family",
        "source_repo": "aoa-techniques",
        "source_catalog": source_catalog,
        "family_ids": list(KAG_SOURCE_LIFT_TECHNIQUE_IDS),
        "entries": payload_entries,
    }
