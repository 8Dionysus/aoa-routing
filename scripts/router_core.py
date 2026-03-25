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
AGENTS_REPO = "aoa-agents"
PLAYBOOKS_REPO = "aoa-playbooks"
KAG_REPO = "aoa-kag"
AOA_ROOT_REPO = "Agents-of-Abyss"
TOS_REPO = "Tree-of-Sophia"
CANONICAL_REPO_BY_KIND = {
    "technique": "aoa-techniques",
    "skill": "aoa-skills",
    "eval": "aoa-evals",
    "memo": "aoa-memo",
}
KNOWN_REPOS = (
    "aoa-routing",
    AOA_ROOT_REPO,
    TOS_REPO,
    AGENTS_REPO,
    PLAYBOOKS_REPO,
    KAG_REPO,
) + tuple(CANONICAL_REPO_BY_KIND.values())
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
MODEL_TIER_SOURCE_REPO = AGENTS_REPO
MODEL_TIER_REGISTRY_PATH = "generated/model_tier_registry.json"
AGENT_REGISTRY_PATH = "generated/agent_registry.min.json"
RUNTIME_SEAM_BINDINGS_PATH = "generated/runtime_seam_bindings.json"
PLAYBOOK_REGISTRY_PATH = "generated/playbook_registry.min.json"
PLAYBOOK_PORTFOLIO_PATH = "docs/PLAYBOOK_PORTFOLIO.md"
FEDERATION_SPINE_PATH = "generated/federation_spine.min.json"
AOA_ECOSYSTEM_REGISTRY_PATH = "generated/ecosystem_registry.min.json"
PAIRING_SURFACE_REPO = "aoa-routing"
PAIRING_SURFACE_FILE = "generated/pairing_hints.min.json"
TINY_MODEL_ENTRYPOINTS_FILE = "generated/tiny_model_entrypoints.json"
FEDERATION_ENTRYPOINTS_FILE = "generated/federation_entrypoints.min.json"
MEMO_INSPECT_SURFACE_FILE = "generated/memory_catalog.min.json"
MEMO_EXPAND_SURFACE_FILE = "generated/memory_sections.full.json"
MEMO_OBJECT_INSPECT_SURFACE_FILE = "generated/memory_object_catalog.min.json"
MEMO_OBJECT_EXPAND_SURFACE_FILE = "generated/memory_object_sections.full.json"
DEFAULT_MEMO_RECALL_MODE = "semantic"
ROUTER_READY_RECALL_CONTRACT_PREFIX = "recall_contract.router."
MEMO_OBJECT_RECALL_FAMILY = "memory_objects"
MEMO_OBJECT_RECALL_DEFAULT_MODE = "working"
MEMO_OBJECT_RECALL_CONTRACTS_BY_MODE = {
    "working": "examples/recall_contract.object.working.json",
    "semantic": "examples/recall_contract.object.semantic.json",
    "lineage": "examples/recall_contract.object.lineage.json",
}
KAG_DEFAULT_ENTRYPOINT_ID = "AOA-T-0019"
FEDERATION_ROOT_IDS = ("aoa-root", "tos-root")
FEDERATION_ACTIVE_ENTRY_KINDS = ("agent", "tier", "playbook", "kag_view")
FEDERATION_DECLARED_ENTRY_KINDS = ("seed", "tos_node", "runtime_surface")
FEDERATION_DEFAULT_AGENT_ENTRY_ID = "AOA-A-0001"
FEDERATION_DEFAULT_TIER_ENTRY_ID = "router"
FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID = "AOA-P-0008"
FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID = "aoa-techniques"
TOS_TINY_ENTRY_ROUTE_PATH = "examples/tos_tiny_entry_route.example.json"
TOS_TINY_ENTRY_ROUTE_ID = "tos-tiny-entry.zarathustra-prologue"
TOS_TINY_ENTRY_PRIMARY_HOP_FIELD = "bounded_hop"
TOS_TINY_ENTRY_LEGACY_HOP_FIELD = "lineage_or_context_hop"
TOS_TINY_ENTRY_DOCTRINE_PATH = "docs/TINY_ENTRY_ROUTE.md"
AOA_TECHNIQUES_KAG_VIEW_ENTRY_SURFACE_REF = (
    "aoa-techniques/generated/repo_doc_surface_manifest.min.json"
)
AOA_TECHNIQUES_KAG_VIEW_OBJECT_SURFACE_REF = "aoa-techniques/generated/technique_catalog.min.json"
AOA_TECHNIQUES_KAG_VIEW_EXAMPLE_OBJECT_IDS = ("AOA-T-0001", "AOA-T-0002", "AOA-T-0003")
TOS_KAG_VIEW_ENTRY_ID = TOS_REPO
TOS_KAG_VIEW_ENTRY_SURFACE_REFS = (
    "Tree-of-Sophia/README.md",
    "Tree-of-Sophia/docs/TINY_ENTRY_ROUTE.md",
)
TOS_KAG_VIEW_OBJECT_SURFACE_REF = "Tree-of-Sophia/examples/tos_tiny_entry_route.example.json"
TOS_KAG_VIEW_PLAYBOOK_ENTRY_ID = "AOA-P-0009"
FALLBACK_ROUTER_KIND = "technique"
TIER_PHASE_ORDER = (
    "route",
    "plan",
    "do",
    "verify",
    "transition",
    "deep",
    "distill",
)
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


def ensure_repo_qualified_ref(value: Any, location: str) -> tuple[str, str]:
    raw_value = ensure_string(value, location)
    repo, separator, ref = raw_value.partition(":")
    if separator != ":":
        raise RouterError(f"{location} must use '<repo>:<path>' form")
    normalized_repo = normalize_repo_name(repo)
    normalized_ref = ensure_repo_relative_path(ref, f"{location}.path")
    return normalized_repo, normalized_ref


def make_repo_qualified_ref(repo: str, relative_path: str) -> str:
    normalized_repo = normalize_repo_name(repo)
    normalized_path = ensure_repo_relative_path(relative_path, f"{normalized_repo}.path")
    return f"{normalized_repo}:{normalized_path}"


def ensure_markdown_file(path: Path, location: str) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RouterError(f"{location} is missing") from exc
    if not text.strip():
        raise RouterError(f"{location} must not be empty")


def ensure_tos_route_surface_path(
    raw_path: Any,
    location: str,
    *,
    tos_root: Path,
    allow_null: bool = False,
) -> str | None:
    if raw_path is None:
        if allow_null:
            return None
        raise RouterError(f"{location} must be a repo-relative Tree-of-Sophia path")
    relative_path = ensure_repo_relative_path(raw_path, location)
    if ":" in relative_path:
        raise RouterError(f"{location} must stay Tree-of-Sophia-relative and must not use repo-qualified refs")
    if relative_path.startswith(("aoa-routing/", "aoa-kag/")):
        raise RouterError(f"{location} must stay inside Tree-of-Sophia and must not point at downstream repos")
    if not (tos_root / relative_path).exists():
        raise RouterError(f"{location} target 'Tree-of-Sophia/{relative_path}' is missing")
    return relative_path


def load_tos_tiny_entry_hop_surface(
    payload: dict[str, Any],
    location: str,
    *,
    tos_root: Path,
) -> str:
    bounded_hop = ensure_tos_route_surface_path(
        payload.get(TOS_TINY_ENTRY_PRIMARY_HOP_FIELD),
        f"{location}.{TOS_TINY_ENTRY_PRIMARY_HOP_FIELD}",
        tos_root=tos_root,
        allow_null=True,
    )
    legacy_hop = ensure_tos_route_surface_path(
        payload.get(TOS_TINY_ENTRY_LEGACY_HOP_FIELD),
        f"{location}.{TOS_TINY_ENTRY_LEGACY_HOP_FIELD}",
        tos_root=tos_root,
        allow_null=True,
    )
    if bounded_hop is None and legacy_hop is None:
        raise RouterError(
            f"{location} must define '{TOS_TINY_ENTRY_PRIMARY_HOP_FIELD}' or "
            f"'{TOS_TINY_ENTRY_LEGACY_HOP_FIELD}'"
        )
    if bounded_hop is not None and legacy_hop is not None and bounded_hop != legacy_hop:
        raise RouterError(
            f"{location}.{TOS_TINY_ENTRY_PRIMARY_HOP_FIELD} and "
            f"{location}.{TOS_TINY_ENTRY_LEGACY_HOP_FIELD} must resolve to the same "
            "Tree-of-Sophia surface during transition"
        )
    return bounded_hop or legacy_hop  # type: ignore[return-value]


def load_tos_tiny_entry_route(tos_root: Path) -> tuple[str, dict[str, Any]]:
    route_path = tos_root / TOS_TINY_ENTRY_ROUTE_PATH
    location = f"{TOS_REPO}/{TOS_TINY_ENTRY_ROUTE_PATH}"
    payload = ensure_mapping(load_json_file(route_path), location)

    route_id = ensure_string(payload.get("route_id"), f"{location}.route_id")
    if route_id != TOS_TINY_ENTRY_ROUTE_ID:
        raise RouterError(
            f"{location}.route_id must stay '{TOS_TINY_ENTRY_ROUTE_ID}' in the current routing wave"
        )

    root_surface = ensure_tos_route_surface_path(
        payload.get("root_surface"),
        f"{location}.root_surface",
        tos_root=tos_root,
    )
    if root_surface != "README.md":
        raise RouterError(f"{location}.root_surface must stay 'README.md' in the current routing wave")

    ensure_string(payload.get("node_kind"), f"{location}.node_kind")
    ensure_string(payload.get("node_id"), f"{location}.node_id")
    ensure_tos_route_surface_path(
        payload.get("capsule_surface"),
        f"{location}.capsule_surface",
        tos_root=tos_root,
    )
    ensure_tos_route_surface_path(
        payload.get("authority_surface"),
        f"{location}.authority_surface",
        tos_root=tos_root,
    )
    load_tos_tiny_entry_hop_surface(payload, location, tos_root=tos_root)
    ensure_tos_route_surface_path(
        payload.get("fallback"),
        f"{location}.fallback",
        tos_root=tos_root,
    )
    ensure_string(payload.get("non_identity_boundary"), f"{location}.non_identity_boundary")
    return TOS_TINY_ENTRY_ROUTE_PATH, payload


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


def load_agent_registry_entries(agents_root: Path) -> tuple[str, list[dict[str, Any]]]:
    registry_path = agents_root / AGENT_REGISTRY_PATH
    location = relative_posix(registry_path, agents_root)
    payload = ensure_mapping(load_json_file(registry_path), location)
    agents = ensure_list(payload.get("agents"), f"{location}.agents")

    entries: list[dict[str, Any]] = []
    for index, item in enumerate(agents):
        agent_location = f"{location}.agents[{index}]"
        agent = ensure_mapping(item, agent_location)
        require_keys(agent, ("id", "name", "summary"), agent_location)
        entries.append(agent)
    return AGENT_REGISTRY_PATH, entries


def load_model_tier_entries(
    agents_root: Path,
    registry_relative_path: str = MODEL_TIER_REGISTRY_PATH,
) -> tuple[str, list[dict[str, Any]]]:
    normalized_path = ensure_repo_relative_path(registry_relative_path, "tier_registry_path")
    registry_path = agents_root / normalized_path
    location = relative_posix(registry_path, agents_root)
    payload = ensure_mapping(load_json_file(registry_path), location)
    model_tiers = ensure_list(payload.get("model_tiers"), f"{location}.model_tiers")

    entries: list[dict[str, Any]] = []
    for index, item in enumerate(model_tiers):
        tier_location = f"{location}.model_tiers[{index}]"
        tier = ensure_mapping(item, tier_location)
        require_keys(tier, ("id", "summary", "artifact_requirement"), tier_location)
        entries.append(tier)
    return normalized_path, entries


def load_runtime_seam_bindings(agents_root: Path) -> tuple[str, list[dict[str, Any]]]:
    bindings_path = agents_root / RUNTIME_SEAM_BINDINGS_PATH
    location = relative_posix(bindings_path, agents_root)
    payload = ensure_mapping(load_json_file(bindings_path), location)
    bindings = ensure_list(payload.get("bindings"), f"{location}.bindings")

    entries: list[dict[str, Any]] = []
    for index, item in enumerate(bindings):
        binding_location = f"{location}.bindings[{index}]"
        binding = ensure_mapping(item, binding_location)
        require_keys(binding, ("phase", "tier_id", "role_names", "artifact_type"), binding_location)
        entries.append(binding)
    return RUNTIME_SEAM_BINDINGS_PATH, entries


def load_playbook_registry_entries(playbooks_root: Path) -> tuple[str, list[dict[str, Any]]]:
    registry_path = playbooks_root / PLAYBOOK_REGISTRY_PATH
    location = relative_posix(registry_path, playbooks_root)
    payload = ensure_mapping(load_json_file(registry_path), location)
    playbooks = ensure_list(payload.get("playbooks"), f"{location}.playbooks")

    entries: list[dict[str, Any]] = []
    for index, item in enumerate(playbooks):
        playbook_location = f"{location}.playbooks[{index}]"
        playbook = ensure_mapping(item, playbook_location)
        require_keys(
            playbook,
            ("id", "name", "summary", "participating_agents", "expected_artifacts"),
            playbook_location,
        )
        entries.append(playbook)
    return PLAYBOOK_REGISTRY_PATH, entries


def load_federation_spine_entries(kag_root: Path) -> tuple[str, list[dict[str, Any]]]:
    spine_path = kag_root / FEDERATION_SPINE_PATH
    location = relative_posix(spine_path, kag_root)
    payload = ensure_mapping(load_json_file(spine_path), location)
    entries = ensure_list(payload.get("repos"), f"{location}.repos")

    # Accept the current compact aoa-kag spine shape while keeping the
    # router-facing KAG view cards stable for this routing wave.
    def normalize_repo_entry(
        repo_entry: dict[str, Any], repo_location: str
    ) -> dict[str, Any]:
        if all(
            key in repo_entry
            for key in (
                "current_entry_surface_refs",
                "current_object_surface_ref",
                "example_object_ids",
            )
        ):
            require_keys(
                repo_entry,
                (
                    "repo",
                    "current_entry_surface_refs",
                    "current_object_surface_ref",
                    "example_object_ids",
                ),
                repo_location,
            )
            return repo_entry

        require_keys(
            repo_entry,
            ("repo", "pilot_posture", "entry_surface_ref", "export_ref", "object_id"),
            repo_location,
        )
        repo_name = normalize_repo_name(
            ensure_string(repo_entry["repo"], f"{repo_location}.repo")
        )
        pilot_posture = ensure_string(
            repo_entry["pilot_posture"], f"{repo_location}.pilot_posture"
        )
        ensure_string(repo_entry["entry_surface_ref"], f"{repo_location}.entry_surface_ref")
        ensure_string(repo_entry["export_ref"], f"{repo_location}.export_ref")
        ensure_string(repo_entry["object_id"], f"{repo_location}.object_id")
        if pilot_posture != "source_owned_export_tiny":
            raise RouterError(
                f"{repo_location}.pilot_posture must stay 'source_owned_export_tiny' in the compact federation spine format"
            )

        if repo_name == FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID:
            return {
                **repo_entry,
                "pilot_posture": "existing_generated_surfaces",
                "current_entry_surface_refs": [
                    AOA_TECHNIQUES_KAG_VIEW_ENTRY_SURFACE_REF
                ],
                "current_object_surface_ref": AOA_TECHNIQUES_KAG_VIEW_OBJECT_SURFACE_REF,
                "example_object_ids": list(AOA_TECHNIQUES_KAG_VIEW_EXAMPLE_OBJECT_IDS),
            }
        if repo_name == TOS_KAG_VIEW_ENTRY_ID:
            return {
                **repo_entry,
                "pilot_posture": "source_owned_tiny_entry_route",
                "current_entry_surface_refs": list(TOS_KAG_VIEW_ENTRY_SURFACE_REFS),
                "current_object_surface_ref": TOS_KAG_VIEW_OBJECT_SURFACE_REF,
                "example_object_ids": [TOS_TINY_ENTRY_ROUTE_ID],
            }
        raise RouterError(
            f"{repo_location}.repo '{repo_name}' is not supported in the compact federation spine format"
        )

    repos: list[dict[str, Any]] = []
    for index, item in enumerate(entries):
        repo_location = f"{location}.repos[{index}]"
        repo_entry = ensure_mapping(item, repo_location)
        repos.append(normalize_repo_entry(repo_entry, repo_location))
    return FEDERATION_SPINE_PATH, repos


def load_ecosystem_registry_entries(aoa_root: Path) -> tuple[str, list[dict[str, Any]]]:
    registry_path = aoa_root / AOA_ECOSYSTEM_REGISTRY_PATH
    location = relative_posix(registry_path, aoa_root)
    payload = ensure_mapping(load_json_file(registry_path), location)
    repos = ensure_list(payload.get("repos"), f"{location}.repos")
    for index, item in enumerate(repos):
        repo_location = f"{location}.repos[{index}]"
        repo_entry = ensure_mapping(item, repo_location)
        require_keys(repo_entry, ("name", "role"), repo_location)
    return AOA_ECOSYSTEM_REGISTRY_PATH, repos


def ensure_cross_repo_surface_ref(value: Any, location: str) -> tuple[str, str]:
    raw_value = ensure_string(value, location)
    repo_name, separator, remainder = raw_value.partition("/")
    if separator != "/":
        raise RouterError(f"{location} must use '<repo>/<path>' form")
    normalized_repo = normalize_repo_name(repo_name)
    normalized_path = ensure_repo_relative_path(remainder, f"{location}.path")
    return normalized_repo, normalized_path


def build_entry_action(
    *,
    verb: str,
    target_repo: str,
    target_surface: str,
    match_key: str,
    target_value: str,
) -> dict[str, str]:
    return {
        "verb": ensure_string(verb, "verb"),
        "target_repo": normalize_repo_name(target_repo),
        "target_surface": ensure_repo_relative_path(target_surface, "target_surface"),
        "match_key": ensure_string(match_key, "match_key"),
        "target_value": ensure_string(target_value, "target_value"),
    }


def build_entry_hop(kind: str, identifier: str) -> dict[str, str]:
    if kind not in FEDERATION_ACTIVE_ENTRY_KINDS:
        raise RouterError(f"unsupported federation entry kind '{kind}'")
    return {
        "kind": kind,
        "id": ensure_string(identifier, f"{kind}.id"),
    }


def title_case_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in value.replace("_", "-").split("-") if part)


def load_repo_doc_manifest_default_doc_id(repo_root: Path, manifest_relative_path: str) -> str:
    manifest_path = repo_root / manifest_relative_path
    location = relative_posix(manifest_path, repo_root)
    payload = ensure_mapping(load_json_file(manifest_path), location)
    docs = ensure_list(payload.get("docs"), f"{location}.docs")
    for index, item in enumerate(docs):
        doc_location = f"{location}.docs[{index}]"
        doc = ensure_mapping(item, doc_location)
        doc_id = ensure_string(doc.get("doc_id"), f"{doc_location}.doc_id")
        if doc_id == "readme":
            return doc_id
    if not docs:
        raise RouterError(f"{location}.docs must not be empty")
    first_doc = ensure_mapping(docs[0], f"{location}.docs[0]")
    return ensure_string(first_doc.get("doc_id"), f"{location}.docs[0].doc_id")


def load_memo_catalog_surfaces(memo_root: Path) -> list[dict[str, Any]]:
    catalog_path = memo_root / MEMO_INSPECT_SURFACE_FILE
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


def load_optional_parallel_memo_recall_families(memo_root: Path) -> dict[str, dict[str, Any]]:
    families: dict[str, dict[str, Any]] = {}
    object_family = load_optional_memo_object_recall_family(memo_root)
    if object_family is not None:
        families[MEMO_OBJECT_RECALL_FAMILY] = object_family
    return families


def load_optional_memo_object_recall_family(memo_root: Path) -> dict[str, Any] | None:
    catalog_path = memo_root / MEMO_OBJECT_INSPECT_SURFACE_FILE
    sections_path = memo_root / MEMO_OBJECT_EXPAND_SURFACE_FILE
    try:
        catalog_payload = ensure_mapping(load_json_file(catalog_path), relative_posix(catalog_path))
        ensure_list(
            catalog_payload.get("memory_objects"),
            f"{relative_posix(catalog_path)}.memory_objects",
        )
        sections_payload = ensure_mapping(
            load_json_file(sections_path),
            relative_posix(sections_path),
        )
        ensure_list(
            sections_payload.get("memory_objects"),
            f"{relative_posix(sections_path)}.memory_objects",
        )
    except RouterError:
        return None

    contracts_by_mode: dict[str, str] = {}
    for mode, relative_contract_path in MEMO_OBJECT_RECALL_CONTRACTS_BY_MODE.items():
        contract_path = memo_root / relative_contract_path
        location = relative_posix(contract_path, memo_root)
        try:
            contract = ensure_mapping(load_json_file(contract_path), location)
            require_keys(
                contract,
                ("mode", "inspect_surface", "expand_surface"),
                location,
            )
            contract_mode = ensure_string(contract["mode"], f"{location}.mode")
            inspect_surface = ensure_repo_relative_path(
                contract["inspect_surface"],
                f"{location}.inspect_surface",
            )
            expand_surface = ensure_repo_relative_path(
                contract["expand_surface"],
                f"{location}.expand_surface",
            )
        except RouterError:
            return None
        if contract_mode != mode:
            return None
        if inspect_surface != MEMO_OBJECT_INSPECT_SURFACE_FILE:
            return None
        if expand_surface != MEMO_OBJECT_EXPAND_SURFACE_FILE:
            return None
        contracts_by_mode[mode] = location

    return {
        "inspect_surface": MEMO_OBJECT_INSPECT_SURFACE_FILE,
        "expand_surface": MEMO_OBJECT_EXPAND_SURFACE_FILE,
        "default_mode": MEMO_OBJECT_RECALL_DEFAULT_MODE,
        "supported_modes": list(MEMO_OBJECT_RECALL_CONTRACTS_BY_MODE.keys()),
        "contracts_by_mode": contracts_by_mode,
    }


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
                    f"{location}.mode must be declared by aoa-memo/{MEMO_INSPECT_SURFACE_FILE}"
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


def build_federation_entrypoints_payload(
    aoa_root: Path,
    techniques_root: Path,
    agents_root: Path,
    playbooks_root: Path,
    kag_root: Path,
    tos_root: Path,
) -> dict[str, Any]:
    load_ecosystem_registry_entries(aoa_root)
    ensure_markdown_file(aoa_root / "README.md", f"{AOA_ROOT_REPO}/README.md")
    ensure_markdown_file(aoa_root / "CHARTER.md", f"{AOA_ROOT_REPO}/CHARTER.md")
    ensure_markdown_file(tos_root / "README.md", f"{TOS_REPO}/README.md")
    ensure_markdown_file(tos_root / "CHARTER.md", f"{TOS_REPO}/CHARTER.md")
    tos_tiny_entry_route_path, tos_tiny_entry_route = load_tos_tiny_entry_route(tos_root)
    ensure_markdown_file(
        tos_root / TOS_TINY_ENTRY_DOCTRINE_PATH,
        f"{TOS_REPO}/{TOS_TINY_ENTRY_DOCTRINE_PATH}",
    )
    ensure_markdown_file(
        kag_root / "docs" / "FEDERATION_SPINE.md",
        f"{KAG_REPO}/docs/FEDERATION_SPINE.md",
    )

    agent_registry_path, agent_entries = load_agent_registry_entries(agents_root)
    model_tier_registry_path, tier_entries = load_model_tier_entries(agents_root)
    runtime_bindings_path, runtime_bindings = load_runtime_seam_bindings(agents_root)
    playbook_registry_path, playbook_entries = load_playbook_registry_entries(playbooks_root)
    federation_spine_path, kag_entries = load_federation_spine_entries(kag_root)

    def bounded_unique(values: Iterable[str], limit: int = 3) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            if value in seen:
                continue
            result.append(value)
            seen.add(value)
            if len(result) >= limit:
                break
        return result

    agent_id_by_name: dict[str, str] = {}
    agent_index: dict[str, dict[str, Any]] = {}
    for index, raw_agent in enumerate(agent_entries):
        location = f"{agent_registry_path}.agents[{index}]"
        agent_id = ensure_string(raw_agent["id"], f"{location}.id")
        agent_name = ensure_string(raw_agent["name"], f"{location}.name")
        agent_id_by_name[agent_name] = agent_id
        agent_index[agent_id] = raw_agent

    tier_index: dict[str, dict[str, Any]] = {}
    artifact_to_tier: dict[str, str] = {}
    for index, raw_tier in enumerate(tier_entries):
        location = f"{model_tier_registry_path}.model_tiers[{index}]"
        tier_id = ensure_string(raw_tier["id"], f"{location}.id")
        artifact_requirement = ensure_string(
            raw_tier["artifact_requirement"],
            f"{location}.artifact_requirement",
        )
        tier_index[tier_id] = raw_tier
        artifact_to_tier[artifact_requirement] = tier_id

    ordered_bindings = sorted(
        runtime_bindings,
        key=lambda binding: (
            TIER_PHASE_ORDER.index(
                ensure_string(
                    binding["phase"],
                    f"{runtime_bindings_path}.bindings.phase",
                )
            )
            if ensure_string(binding["phase"], f"{runtime_bindings_path}.bindings.phase")
            in TIER_PHASE_ORDER
            else len(TIER_PHASE_ORDER),
            ensure_string(binding["tier_id"], f"{runtime_bindings_path}.bindings.tier_id"),
        ),
    )
    tier_ids_by_agent_name: dict[str, list[str]] = {}
    agent_ids_by_tier: dict[str, list[str]] = {}
    for index, raw_binding in enumerate(ordered_bindings):
        location = f"{runtime_bindings_path}.bindings[{index}]"
        tier_id = ensure_string(raw_binding["tier_id"], f"{location}.tier_id")
        role_names = ensure_string_list(raw_binding["role_names"], f"{location}.role_names")
        for role_name in role_names:
            tier_ids_by_agent_name.setdefault(role_name, []).append(tier_id)
            agent_id = agent_id_by_name.get(role_name)
            if agent_id is not None:
                agent_ids_by_tier.setdefault(tier_id, []).append(agent_id)

    for agent_id in (FEDERATION_DEFAULT_AGENT_ENTRY_ID,):
        if agent_id not in agent_index:
            raise RouterError(f"federation entry ABI requires agent '{agent_id}'")
    for tier_id in (FEDERATION_DEFAULT_TIER_ENTRY_ID,):
        if tier_id not in tier_index:
            raise RouterError(f"federation entry ABI requires tier '{tier_id}'")

    playbook_index: dict[str, dict[str, Any]] = {}
    for index, raw_playbook in enumerate(playbook_entries):
        location = f"{playbook_registry_path}.playbooks[{index}]"
        playbook_id = ensure_string(raw_playbook["id"], f"{location}.id")
        playbook_index[playbook_id] = raw_playbook
    if FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID not in playbook_index:
        raise RouterError(
            f"federation entry ABI requires playbook '{FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID}'"
        )
    if "AOA-P-0009" not in playbook_index:
        raise RouterError("federation entry ABI requires playbook 'AOA-P-0009'")

    kag_index: dict[str, dict[str, Any]] = {}
    for index, raw_kag_entry in enumerate(kag_entries):
        location = f"{federation_spine_path}.repos[{index}]"
        repo_name = normalize_repo_name(
            ensure_string(raw_kag_entry["repo"], f"{location}.repo")
        )
        kag_index[repo_name] = raw_kag_entry
    if FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID not in kag_index:
        raise RouterError(
            f"federation entry ABI requires KAG view '{FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID}'"
        )
    if TOS_KAG_VIEW_ENTRY_ID not in kag_index:
        raise RouterError(
            f"federation entry ABI requires KAG view '{TOS_KAG_VIEW_ENTRY_ID}'"
        )
    unsupported_kag_view_ids = set(kag_index) - {
        FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID,
        TOS_KAG_VIEW_ENTRY_ID,
    }
    if unsupported_kag_view_ids:
        unsupported = ", ".join(sorted(unsupported_kag_view_ids))
        raise RouterError(
            "current federation entry ABI only supports explicit KAG views for "
            f"{FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID} and {TOS_KAG_VIEW_ENTRY_ID}; got {unsupported}"
        )

    federation_entrypoints: list[dict[str, Any]] = []

    for agent_id in sorted(agent_index):
        agent = agent_index[agent_id]
        agent_name = ensure_string(agent["name"], f"{agent_id}.name")
        authority_path = f"profiles/{agent_name}.profile.json"
        ensure_mapping(
            load_json_file(agents_root / authority_path),
            f"{AGENTS_REPO}/{authority_path}",
        )
        related_tiers = bounded_unique(tier_ids_by_agent_name.get(agent_name, []))
        if not related_tiers:
            related_tiers = [FEDERATION_DEFAULT_TIER_ENTRY_ID]
        federation_entrypoints.append(
            {
                "kind": "agent",
                "id": agent_id,
                "owner_repo": AGENTS_REPO,
                "title": f"{title_case_slug(agent_name)} Agent",
                "capsule_surface": make_repo_qualified_ref(AGENTS_REPO, AGENT_REGISTRY_PATH),
                "authority_surface": make_repo_qualified_ref(AGENTS_REPO, authority_path),
                "next_actions": [
                    build_entry_action(
                        verb="inspect",
                        target_repo=PAIRING_SURFACE_REPO,
                        target_surface=FEDERATION_ENTRYPOINTS_FILE,
                        match_key="id",
                        target_value=tier_id,
                    )
                    for tier_id in related_tiers
                ],
                "fallback": build_entry_action(
                    verb="inspect",
                    target_repo=PAIRING_SURFACE_REPO,
                    target_surface=FEDERATION_ENTRYPOINTS_FILE,
                    match_key="id",
                    target_value=related_tiers[0],
                ),
                "risk": "Agent entry cards summarize role posture; confirm the source profile before treating a handoff hint as binding.",
                "next_hops": [build_entry_hop("tier", tier_id) for tier_id in related_tiers],
            }
        )

    for tier_id in sorted(tier_index):
        authority_path = f"model_tiers/{tier_id}.tier.json"
        ensure_mapping(
            load_json_file(agents_root / authority_path),
            f"{AGENTS_REPO}/{authority_path}",
        )
        related_agents = bounded_unique(agent_ids_by_tier.get(tier_id, []))
        if not related_agents:
            related_agents = [FEDERATION_DEFAULT_AGENT_ENTRY_ID]
        federation_entrypoints.append(
            {
                "kind": "tier",
                "id": tier_id,
                "owner_repo": AGENTS_REPO,
                "title": f"{title_case_slug(tier_id)} Tier",
                "capsule_surface": make_repo_qualified_ref(
                    AGENTS_REPO, MODEL_TIER_REGISTRY_PATH
                ),
                "authority_surface": make_repo_qualified_ref(AGENTS_REPO, authority_path),
                "next_actions": [
                    build_entry_action(
                        verb="inspect",
                        target_repo=PAIRING_SURFACE_REPO,
                        target_surface=FEDERATION_ENTRYPOINTS_FILE,
                        match_key="id",
                        target_value=agent_id,
                    )
                    for agent_id in related_agents
                ],
                "fallback": build_entry_action(
                    verb="inspect",
                    target_repo=PAIRING_SURFACE_REPO,
                    target_surface=FEDERATION_ENTRYPOINTS_FILE,
                    match_key="id",
                    target_value=related_agents[0],
                ),
                "risk": "Tier entry cards orient effort class and handoff posture; the tier contract remains authoritative in aoa-agents.",
                "next_hops": [build_entry_hop("agent", agent_id) for agent_id in related_agents],
            }
        )

    for playbook_id in sorted(playbook_index):
        playbook = playbook_index[playbook_id]
        playbook_name = ensure_string(playbook["name"], f"{playbook_id}.name")
        candidate_authority_path = f"playbooks/{playbook_name}/PLAYBOOK.md"
        authority_path = candidate_authority_path
        if not (playbooks_root / authority_path).exists():
            authority_path = PLAYBOOK_PORTFOLIO_PATH
        ensure_markdown_file(playbooks_root / authority_path, f"{PLAYBOOKS_REPO}/{authority_path}")

        expected_artifacts = ensure_string_list(
            playbook["expected_artifacts"],
            f"{playbook_id}.expected_artifacts",
        )
        participating_agents = ensure_string_list(
            playbook["participating_agents"],
            f"{playbook_id}.participating_agents",
        )
        next_hops: list[dict[str, str]] = []
        next_actions: list[dict[str, str]] = []

        tier_hops = bounded_unique(
            artifact_to_tier[artifact]
            for artifact in expected_artifacts
            if artifact in artifact_to_tier
        )
        if tier_hops:
            next_hops = [build_entry_hop("tier", tier_id) for tier_id in tier_hops]
            next_actions = [
                build_entry_action(
                    verb="inspect",
                    target_repo=PAIRING_SURFACE_REPO,
                    target_surface=FEDERATION_ENTRYPOINTS_FILE,
                    match_key="id",
                    target_value=tier_id,
                )
                for tier_id in tier_hops
            ]
        else:
            agent_hops = bounded_unique(
                agent_id_by_name[agent_name]
                for agent_name in participating_agents
                if agent_name in agent_id_by_name
            )
            if not agent_hops:
                agent_hops = [FEDERATION_DEFAULT_AGENT_ENTRY_ID]
            next_hops = [build_entry_hop("agent", agent_id) for agent_id in agent_hops]
            next_actions = [
                build_entry_action(
                    verb="inspect",
                    target_repo=PAIRING_SURFACE_REPO,
                    target_surface=FEDERATION_ENTRYPOINTS_FILE,
                    match_key="id",
                    target_value=agent_id,
                )
                for agent_id in agent_hops
            ]

        fallback_target = next_actions[0]["target_value"]
        federation_entrypoints.append(
            {
                "kind": "playbook",
                "id": playbook_id,
                "owner_repo": PLAYBOOKS_REPO,
                "title": title_case_slug(playbook_name),
                "capsule_surface": make_repo_qualified_ref(
                    PLAYBOOKS_REPO, PLAYBOOK_REGISTRY_PATH
                ),
                "authority_surface": make_repo_qualified_ref(PLAYBOOKS_REPO, authority_path),
                "next_actions": next_actions,
                "fallback": build_entry_action(
                    verb="inspect",
                    target_repo=PAIRING_SURFACE_REPO,
                    target_surface=FEDERATION_ENTRYPOINTS_FILE,
                    match_key="id",
                    target_value=fallback_target,
                ),
                "risk": "Playbook entry cards compress scenario posture; read the source playbook bundle or portfolio doc before using the route as execution authority.",
                "next_hops": next_hops,
            }
        )

    for kag_view_id in sorted(kag_index):
        kag_entry = kag_index[kag_view_id]
        pilot_posture = ensure_string(
            kag_entry.get("pilot_posture"),
            f"{kag_view_id}.pilot_posture",
        )
        entry_surface_refs = ensure_string_list(
            kag_entry["current_entry_surface_refs"],
            f"{kag_view_id}.current_entry_surface_refs",
        )
        object_surface_ref = ensure_string(
            kag_entry["current_object_surface_ref"],
            f"{kag_view_id}.current_object_surface_ref",
        )
        example_object_ids = ensure_string_list(
            kag_entry["example_object_ids"],
            f"{kag_view_id}.example_object_ids",
        )
        if not example_object_ids:
            raise RouterError(f"{kag_view_id}.example_object_ids must not be empty")
        if kag_view_id == FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID:
            if pilot_posture != "existing_generated_surfaces":
                raise RouterError(
                    f"{kag_view_id}.pilot_posture must stay 'existing_generated_surfaces' in the current routing wave"
                )
            if entry_surface_refs != [AOA_TECHNIQUES_KAG_VIEW_ENTRY_SURFACE_REF]:
                raise RouterError(
                    f"{kag_view_id}.current_entry_surface_refs must stay '{AOA_TECHNIQUES_KAG_VIEW_ENTRY_SURFACE_REF}' in the current routing wave"
                )
            if object_surface_ref != AOA_TECHNIQUES_KAG_VIEW_OBJECT_SURFACE_REF:
                raise RouterError(
                    f"{kag_view_id}.current_object_surface_ref must stay '{AOA_TECHNIQUES_KAG_VIEW_OBJECT_SURFACE_REF}' in the current routing wave"
                )
            if example_object_ids != list(AOA_TECHNIQUES_KAG_VIEW_EXAMPLE_OBJECT_IDS):
                raise RouterError(
                    f"{kag_view_id}.example_object_ids must stay {list(AOA_TECHNIQUES_KAG_VIEW_EXAMPLE_OBJECT_IDS)!r} in the current routing wave"
                )
            entry_target_repo, entry_target_surface = ensure_cross_repo_surface_ref(
                entry_surface_refs[0],
                f"{kag_view_id}.current_entry_surface_refs[0]",
            )
            object_target_repo, object_target_surface = ensure_cross_repo_surface_ref(
                object_surface_ref,
                f"{kag_view_id}.current_object_surface_ref",
            )
            entry_doc_id = load_repo_doc_manifest_default_doc_id(
                techniques_root,
                entry_target_surface,
            )
            title = f"{title_case_slug(kag_view_id)} Readiness View"
            next_actions = [
                build_entry_action(
                    verb="inspect",
                    target_repo=entry_target_repo,
                    target_surface=entry_target_surface,
                    match_key="doc_id",
                    target_value=entry_doc_id,
                ),
                build_entry_action(
                    verb="inspect",
                    target_repo=object_target_repo,
                    target_surface=object_target_surface,
                    match_key="id",
                    target_value=example_object_ids[0],
                ),
            ]
            risk = "KAG view cards summarize derived readiness and current source-facing surfaces; confirm aoa-kag doctrine and the owning repo before treating the view as canon."
            next_hops = [
                build_entry_hop("tier", FEDERATION_DEFAULT_TIER_ENTRY_ID),
                build_entry_hop("playbook", FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID),
            ]
        elif kag_view_id == TOS_KAG_VIEW_ENTRY_ID:
            if pilot_posture != "source_owned_tiny_entry_route":
                raise RouterError(
                    f"{kag_view_id}.pilot_posture must stay 'source_owned_tiny_entry_route' in the current routing wave"
                )
            if entry_surface_refs != list(TOS_KAG_VIEW_ENTRY_SURFACE_REFS):
                raise RouterError(
                    f"{kag_view_id}.current_entry_surface_refs must stay {list(TOS_KAG_VIEW_ENTRY_SURFACE_REFS)!r} in the current routing wave"
                )
            if object_surface_ref != TOS_KAG_VIEW_OBJECT_SURFACE_REF:
                raise RouterError(
                    f"{kag_view_id}.current_object_surface_ref must stay '{TOS_KAG_VIEW_OBJECT_SURFACE_REF}' in the current routing wave"
                )
            if example_object_ids != [TOS_TINY_ENTRY_ROUTE_ID]:
                raise RouterError(
                    f"{kag_view_id}.example_object_ids must stay ['{TOS_TINY_ENTRY_ROUTE_ID}'] in the current routing wave"
                )
            title = "Tree-of-Sophia Readiness View"
            next_actions = [
                build_entry_action(
                    verb="inspect",
                    target_repo=TOS_REPO,
                    target_surface=TOS_TINY_ENTRY_DOCTRINE_PATH,
                    match_key="path",
                    target_value=TOS_TINY_ENTRY_DOCTRINE_PATH,
                ),
                build_entry_action(
                    verb="inspect",
                    target_repo=TOS_REPO,
                    target_surface=tos_tiny_entry_route_path,
                    match_key="route_id",
                    target_value=TOS_TINY_ENTRY_ROUTE_ID,
                ),
            ]
            risk = "KAG view cards summarize derived readiness and current source-facing surfaces; Tree-of-Sophia remains authoritative for ToS meaning while this derived view only orients entry through the current tiny-entry seam."
            next_hops = [
                build_entry_hop("tier", FEDERATION_DEFAULT_TIER_ENTRY_ID),
                build_entry_hop("playbook", TOS_KAG_VIEW_PLAYBOOK_ENTRY_ID),
            ]
        else:
            raise RouterError(f"unsupported KAG view '{kag_view_id}'")
        federation_entrypoints.append(
            {
                "kind": "kag_view",
                "id": kag_view_id,
                "owner_repo": KAG_REPO,
                "title": title,
                "capsule_surface": make_repo_qualified_ref(KAG_REPO, FEDERATION_SPINE_PATH),
                "authority_surface": make_repo_qualified_ref(
                    KAG_REPO, "docs/FEDERATION_SPINE.md"
                ),
                "next_actions": next_actions,
                "fallback": build_entry_action(
                    verb="inspect",
                    target_repo=PAIRING_SURFACE_REPO,
                    target_surface=FEDERATION_ENTRYPOINTS_FILE,
                    match_key="id",
                    target_value=FEDERATION_DEFAULT_TIER_ENTRY_ID,
                ),
                "risk": risk,
                "next_hops": next_hops,
            }
        )

    return {
        "version": 1,
        "source_inputs": [
            {
                "name": "aoa_root_readme",
                "repo": AOA_ROOT_REPO,
                "role": "root_entry",
                "ref": "README.md",
            },
            {
                "name": "tos_root_readme",
                "repo": TOS_REPO,
                "role": "root_entry",
                "ref": "README.md",
            },
            {
                "name": "tos_tiny_entry_route",
                "repo": TOS_REPO,
                "role": "tiny_entry_handoff",
                "ref": tos_tiny_entry_route_path,
            },
            {
                "name": "agent_registry",
                "repo": AGENTS_REPO,
                "role": "agent_entries",
                "ref": agent_registry_path,
            },
            {
                "name": "model_tier_registry",
                "repo": AGENTS_REPO,
                "role": "tier_entries",
                "ref": model_tier_registry_path,
            },
            {
                "name": "runtime_seam_bindings",
                "repo": AGENTS_REPO,
                "role": "tier_role_bindings",
                "ref": runtime_bindings_path,
            },
            {
                "name": "playbook_registry",
                "repo": PLAYBOOKS_REPO,
                "role": "playbook_entries",
                "ref": playbook_registry_path,
            },
            {
                "name": "federation_spine",
                "repo": KAG_REPO,
                "role": "kag_views",
                "ref": federation_spine_path,
            },
        ],
        "root_entries": [
            {
                "id": "aoa-root",
                "owner_repo": AOA_ROOT_REPO,
                "title": "AoA Federation Root",
                "capsule_surface": make_repo_qualified_ref(AOA_ROOT_REPO, "README.md"),
                "authority_surface": make_repo_qualified_ref(AOA_ROOT_REPO, "CHARTER.md"),
                "next_actions": [
                    build_entry_action(
                        verb="inspect",
                        target_repo=PAIRING_SURFACE_REPO,
                        target_surface=FEDERATION_ENTRYPOINTS_FILE,
                        match_key="id",
                        target_value=FEDERATION_DEFAULT_TIER_ENTRY_ID,
                    ),
                    build_entry_action(
                        verb="inspect",
                        target_repo=PAIRING_SURFACE_REPO,
                        target_surface=FEDERATION_ENTRYPOINTS_FILE,
                        match_key="id",
                        target_value=FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID,
                    ),
                    build_entry_action(
                        verb="inspect",
                        target_repo=PAIRING_SURFACE_REPO,
                        target_surface=FEDERATION_ENTRYPOINTS_FILE,
                        match_key="id",
                        target_value=FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID,
                    ),
                ],
                "fallback": build_entry_action(
                    verb="pick",
                    target_repo=PAIRING_SURFACE_REPO,
                    target_surface="generated/aoa_router.min.json",
                    match_key="kind",
                    target_value=FALLBACK_ROUTER_KIND,
                ),
                "risk": "AoA root orientation can be mistaken for source authority; use the source charter and owning repo surfaces before treating a route card as canon.",
                "next_hops": [
                    build_entry_hop("tier", FEDERATION_DEFAULT_TIER_ENTRY_ID),
                    build_entry_hop("playbook", FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID),
                    build_entry_hop("kag_view", FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID),
                ],
            },
            {
                "id": "tos-root",
                "owner_repo": TOS_REPO,
                "title": "ToS Federation Root",
                "capsule_surface": make_repo_qualified_ref(TOS_REPO, "README.md"),
                "authority_surface": make_repo_qualified_ref(TOS_REPO, "CHARTER.md"),
                "next_actions": [
                    build_entry_action(
                        verb="inspect",
                        target_repo=TOS_REPO,
                        target_surface=tos_tiny_entry_route_path,
                        match_key="route_id",
                        target_value=ensure_string(
                            tos_tiny_entry_route["route_id"],
                            f"{TOS_REPO}/{tos_tiny_entry_route_path}.route_id",
                        ),
                    ),
                    build_entry_action(
                        verb="inspect",
                        target_repo=PAIRING_SURFACE_REPO,
                        target_surface=FEDERATION_ENTRYPOINTS_FILE,
                        match_key="id",
                        target_value=TOS_KAG_VIEW_ENTRY_ID,
                    ),
                    build_entry_action(
                        verb="inspect",
                        target_repo=PAIRING_SURFACE_REPO,
                        target_surface=FEDERATION_ENTRYPOINTS_FILE,
                        match_key="id",
                        target_value="AOA-P-0009",
                    ),
                ],
                "fallback": build_entry_action(
                    verb="inspect",
                    target_repo=PAIRING_SURFACE_REPO,
                    target_surface=FEDERATION_ENTRYPOINTS_FILE,
                    match_key="id",
                    target_value="aoa-root",
                ),
                "risk": "ToS root orientation must keep Tree-of-Sophia authority in the charter while handing off to one source-owned tiny-entry route; downstream routing, KAG, and playbook hops remain secondary orientation rather than ToS authority replacement.",
                "next_hops": [
                    build_entry_hop("kag_view", TOS_KAG_VIEW_ENTRY_ID),
                    build_entry_hop("playbook", TOS_KAG_VIEW_PLAYBOOK_ENTRY_ID),
                ],
            },
        ],
        "active_entry_kinds": list(FEDERATION_ACTIVE_ENTRY_KINDS),
        "declared_entry_kinds": list(FEDERATION_DECLARED_ENTRY_KINDS),
        "entrypoints": sorted(
            federation_entrypoints,
            key=lambda entry: (
                FEDERATION_ACTIVE_ENTRY_KINDS.index(entry["kind"]),
                entry["id"],
            ),
        ),
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
        recall_parallel_families: dict[str, dict[str, Any]] | None = None,
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
            if recall_parallel_families:
                recall["parallel_families"] = {
                    family_name: dict(family_payload)
                    for family_name, family_payload in sorted(recall_parallel_families.items())
                }
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
    recall_parallel_families = load_optional_parallel_memo_recall_families(memo_root)
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
                    surface_file=MEMO_INSPECT_SURFACE_FILE,
                    match_field="id",
                    expand_enabled=True,
                    expand_surface_file=MEMO_EXPAND_SURFACE_FILE,
                    expand_match_field="id",
                    expand_section_key_field="section_id",
                    default_sections=[],
                    supported_sections=[],
                    recall_enabled=bool(recall_supported_modes),
                    recall_contract_file=recall_contract_file,
                    recall_default_mode=recall_default_mode,
                    recall_supported_modes=recall_supported_modes,
                    recall_contracts_by_mode=recall_contracts_by_mode,
                    recall_parallel_families=recall_parallel_families,
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
    federation_payload: dict[str, Any],
) -> dict[str, Any]:
    registry_index = {(entry["kind"], entry["id"]): entry for entry in registry_entries}
    available_kinds = {entry["kind"] for entry in registry_entries}
    hints = ensure_list(hints_payload.get("hints"), "task_to_surface_hints.json.hints")
    federation_root_entries = ensure_list(
        federation_payload.get("root_entries"),
        "federation_entrypoints.min.json.root_entries",
    )
    federation_entries = ensure_list(
        federation_payload.get("entrypoints"),
        "federation_entrypoints.min.json.entrypoints",
    )
    active_entry_kinds = ensure_string_list(
        federation_payload.get("active_entry_kinds"),
        "federation_entrypoints.min.json.active_entry_kinds",
    )
    memo_recall_supported_modes: list[str] = []
    memo_parallel_recall_modes: dict[str, list[str]] = {}
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
                parallel_families = recall.get("parallel_families")
                if parallel_families is not None:
                    parallel_family_payloads = ensure_mapping(
                        parallel_families,
                        f"{location}.actions.recall.parallel_families",
                    )
                    for family_name, raw_family in sorted(parallel_family_payloads.items()):
                        family_location = (
                            f"{location}.actions.recall.parallel_families.{family_name}"
                        )
                        family_payload = ensure_mapping(raw_family, family_location)
                        memo_parallel_recall_modes[family_name] = ensure_string_list(
                            family_payload.get("supported_modes"),
                            f"{family_location}.supported_modes",
                        )
                        queries.append(
                            {
                                "verb": "recall",
                                "source_repo": PAIRING_SURFACE_REPO,
                                "target_surface": "generated/task_to_surface_hints.json",
                                "match_key": "kind",
                                "allowed_kinds": [kind],
                                "recall_family": family_name,
                            }
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
    for family_name, supported_modes in sorted(memo_parallel_recall_modes.items()):
        starter_prefix = f"memo-{family_name.replace('_', '-')}-recall"
        if family_name == MEMO_OBJECT_RECALL_FAMILY:
            starter_prefix = "memo-object-recall"
        for mode in supported_modes:
            starters.append(
                {
                    "name": f"{starter_prefix}-{mode.replace('_', '-')}",
                    "verb": "recall",
                    "source_repo": PAIRING_SURFACE_REPO,
                    "target_surface": "generated/task_to_surface_hints.json",
                    "match_key": "kind",
                    "allowed_kinds": ["memo"],
                    "target_kind": "memo",
                    "target_value": "memo",
                    "recall_family": family_name,
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

    root_ids = [
        ensure_string(entry.get("id"), f"federation_entrypoints.min.json.root_entries[{index}].id")
        for index, entry in enumerate(federation_root_entries)
        if isinstance(entry, dict)
    ]
    federation_entry_ids_by_kind: dict[str, list[str]] = {}
    for index, raw_entry in enumerate(federation_entries):
        location = f"federation_entrypoints.min.json.entrypoints[{index}]"
        entry = ensure_mapping(raw_entry, location)
        entry_kind = ensure_string(entry.get("kind"), f"{location}.kind")
        entry_id = ensure_string(entry.get("id"), f"{location}.id")
        federation_entry_ids_by_kind.setdefault(entry_kind, []).append(entry_id)

    if FEDERATION_DEFAULT_AGENT_ENTRY_ID not in federation_entry_ids_by_kind.get("agent", []):
        raise RouterError(
            f"tiny-model federation seam requires agent '{FEDERATION_DEFAULT_AGENT_ENTRY_ID}'"
        )
    if FEDERATION_DEFAULT_TIER_ENTRY_ID not in federation_entry_ids_by_kind.get("tier", []):
        raise RouterError(
            f"tiny-model federation seam requires tier '{FEDERATION_DEFAULT_TIER_ENTRY_ID}'"
        )
    if FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID not in federation_entry_ids_by_kind.get("playbook", []):
        raise RouterError(
            f"tiny-model federation seam requires playbook '{FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID}'"
        )
    if FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID not in federation_entry_ids_by_kind.get("kag_view", []):
        raise RouterError(
            f"tiny-model federation seam requires KAG view '{FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID}'"
        )

    federation_queries: list[dict[str, Any]] = [
        {
            "name": "federation-kind-pick",
            "verb": "pick",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "kind",
            "allowed_entry_kinds": active_entry_kinds,
        },
        {
            "name": "federation-entry-inspect",
            "verb": "inspect",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "id",
            "allowed_entry_kinds": active_entry_kinds,
        },
        {
            "name": "federation-root-inspect",
            "verb": "inspect",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "id",
            "allowed_root_ids": root_ids,
        },
    ]
    federation_starters: list[dict[str, Any]] = [
        {
            "name": "federation-root",
            "verb": "pick",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
        },
        {
            "name": "aoa-root",
            "verb": "inspect",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "id",
            "target_value": "aoa-root",
        },
        {
            "name": "tos-root",
            "verb": "inspect",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "id",
            "target_value": "tos-root",
        },
        {
            "name": "agent-root",
            "verb": "inspect",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "id",
            "target_value": FEDERATION_DEFAULT_AGENT_ENTRY_ID,
            "entry_kind": "agent",
        },
        {
            "name": "tier-root",
            "verb": "inspect",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "id",
            "target_value": FEDERATION_DEFAULT_TIER_ENTRY_ID,
            "entry_kind": "tier",
        },
        {
            "name": "playbook-root",
            "verb": "inspect",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "id",
            "target_value": FEDERATION_DEFAULT_PLAYBOOK_ENTRY_ID,
            "entry_kind": "playbook",
        },
        {
            "name": "kag-view-root",
            "verb": "inspect",
            "source_repo": PAIRING_SURFACE_REPO,
            "target_surface": FEDERATION_ENTRYPOINTS_FILE,
            "match_key": "id",
            "target_value": FEDERATION_DEFAULT_KAG_VIEW_ENTRY_ID,
            "entry_kind": "kag_view",
        },
    ]

    return {
        "version": 2,
        "queries": queries,
        "starters": starters,
        "federation_queries": federation_queries,
        "federation_starters": federation_starters,
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
