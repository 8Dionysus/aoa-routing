#!/usr/bin/env python3
"""Build derived routing surfaces for aoa-routing."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from router_core import (
    CANONICAL_REPO_BY_KIND,
    REPO_ROOT,
    RouterError,
    build_recommended_paths_payload,
    build_router_payload,
    build_task_to_surface_hints_payload,
    ensure_bool,
    ensure_int,
    ensure_list,
    ensure_mapping,
    ensure_repo_relative_path,
    ensure_string,
    ensure_string_list,
    load_json_file,
    relative_posix,
    require_keys,
    sort_registry_entries,
    write_json_file,
)


TECHNIQUE_SOURCE_TYPE = "generated-catalog"
SKILL_SOURCE_TYPE = "generated-catalog"
EVAL_SOURCE_TYPE = "generated-catalog"


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
        help="Path to the aoa-memo repository root. Reserved only in v0.1.",
    )
    parser.add_argument(
        "--generated-dir",
        type=Path,
        default=REPO_ROOT / "generated",
        help="Directory where generated outputs should be written.",
    )
    return parser.parse_args()


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


def build_outputs(
    techniques_root: Path,
    skills_root: Path,
    evals_root: Path,
    memo_root: Path,
) -> dict[str, dict[str, Any]]:
    _ = memo_root
    registry_entries = sort_registry_entries(
        collect_technique_entries(techniques_root)
        + collect_skill_entries(skills_root)
        + collect_eval_entries(evals_root)
    )
    seen: set[tuple[str, str]] = set()
    for entry in registry_entries:
        key = (entry["kind"], entry["id"])
        if key in seen:
            raise RouterError(f"duplicate registry entry for {entry['kind']}:{entry['id']}")
        seen.add(key)

    registry_payload = {
        "registry_version": 1,
        "reserved_kinds": ["memo"],
        "entries": registry_entries,
    }
    router_payload = build_router_payload(registry_entries)
    hints_payload = build_task_to_surface_hints_payload()
    recommended_payload = build_recommended_paths_payload(registry_entries)
    return {
        "cross_repo_registry.min.json": registry_payload,
        "aoa_router.min.json": router_payload,
        "task_to_surface_hints.json": hints_payload,
        "recommended_paths.min.json": recommended_payload,
    }


def main() -> int:
    args = parse_args()
    outputs = build_outputs(
        args.techniques_root.resolve(),
        args.skills_root.resolve(),
        args.evals_root.resolve(),
        args.memo_root.resolve(),
    )
    generated_dir = args.generated_dir.resolve()
    generated_dir.mkdir(parents=True, exist_ok=True)

    for filename, payload in outputs.items():
        path = generated_dir / filename
        write_json_file(path, payload)
        print(f"[ok] wrote {relative_posix(path)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RouterError as exc:
        print(f"[error] {exc}")
        raise SystemExit(1)
