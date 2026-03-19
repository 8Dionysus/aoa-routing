#!/usr/bin/env python3
"""Build derived routing surfaces for aoa-routing."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from router_core import (
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
    is_pending_technique_id,
    load_json_file,
    load_yaml_file,
    normalize_repo_name,
    parse_frontmatter_markdown,
    relative_posix,
    require_keys,
    sort_registry_entries,
    write_json_file,
)


TECHNIQUE_SOURCE_TYPE = "generated-catalog"
HYBRID_SOURCE_TYPE = "markdown-frontmatter+manifest"


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
                "repo": "aoa-techniques",
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
    skills_dir = skills_root / "skills"
    if not skills_dir.is_dir():
        raise RouterError(f"{relative_posix(skills_dir)} is missing")

    entries: list[dict[str, Any]] = []
    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        skill_md_path = skill_dir / "SKILL.md"
        techniques_path = skill_dir / "techniques.yaml"

        metadata, _body = parse_frontmatter_markdown(skill_md_path)
        metadata = ensure_mapping(metadata, relative_posix(skill_md_path))
        require_keys(
            metadata,
            ("name", "scope", "status", "summary", "invocation_mode", "technique_dependencies"),
            relative_posix(skill_md_path),
        )

        manifest = ensure_mapping(
            load_yaml_file(techniques_path),
            relative_posix(techniques_path),
        )
        require_keys(manifest, ("skill_name", "techniques"), relative_posix(techniques_path))

        skill_name = ensure_string(metadata["name"], f"{relative_posix(skill_md_path)}.name")
        if skill_name != skill_dir.name:
            raise RouterError(
                f"{relative_posix(skill_md_path)} frontmatter name '{skill_name}' does not match directory '{skill_dir.name}'"
            )
        manifest_name = ensure_string(
            manifest["skill_name"], f"{relative_posix(techniques_path)}.skill_name"
        )
        if manifest_name != skill_name:
            raise RouterError(
                f"{relative_posix(techniques_path)} skill_name '{manifest_name}' does not match '{skill_name}'"
            )

        frontmatter_dependency_ids = ensure_string_list(
            metadata["technique_dependencies"],
            f"{relative_posix(skill_md_path)}.technique_dependencies",
        )
        manifest_techniques = ensure_list(
            manifest["techniques"], f"{relative_posix(techniques_path)}.techniques"
        )
        manifest_dependency_ids: list[str] = []
        for index, item in enumerate(manifest_techniques):
            location = f"{relative_posix(techniques_path)}.techniques[{index}]"
            dependency = ensure_mapping(item, location)
            require_keys(dependency, ("id", "repo", "path"), location)
            dependency_id = ensure_string(dependency["id"], f"{location}.id")
            manifest_dependency_ids.append(dependency_id)
            repo_name = normalize_repo_name(ensure_string(dependency["repo"], f"{location}.repo"))
            if repo_name != "aoa-techniques":
                raise RouterError(f"{location}.repo must resolve to aoa-techniques")
            raw_path = ensure_string(dependency["path"], f"{location}.path")
            if is_pending_technique_id(dependency_id):
                if raw_path != "TBD":
                    ensure_repo_relative_path(raw_path, f"{location}.path")
            else:
                ensure_repo_relative_path(raw_path, f"{location}.path")

        if frontmatter_dependency_ids != manifest_dependency_ids:
            raise RouterError(
                f"{relative_posix(skill_md_path)} technique_dependencies do not match {relative_posix(techniques_path)}"
            )

        entries.append(
            {
                "kind": "skill",
                "id": skill_name,
                "name": skill_name,
                "repo": "aoa-skills",
                "path": skill_md_path.relative_to(skills_root).as_posix(),
                "status": ensure_string(metadata["status"], f"{relative_posix(skill_md_path)}.status"),
                "summary": ensure_string(metadata["summary"], f"{relative_posix(skill_md_path)}.summary"),
                "source_type": HYBRID_SOURCE_TYPE,
                "attributes": {
                    "scope": ensure_string(metadata["scope"], f"{relative_posix(skill_md_path)}.scope"),
                    "invocation_mode": ensure_string(
                        metadata["invocation_mode"],
                        f"{relative_posix(skill_md_path)}.invocation_mode",
                    ),
                    "technique_dependencies": frontmatter_dependency_ids,
                },
            }
        )
    return entries


def compare_eval_field(
    metadata: dict[str, Any],
    manifest: dict[str, Any],
    field_name: str,
    eval_md_path: Path,
    eval_yaml_path: Path,
) -> Any:
    left = metadata.get(field_name)
    right = manifest.get(field_name)
    if left != right:
        raise RouterError(
            f"{relative_posix(eval_md_path)} field '{field_name}' does not match {relative_posix(eval_yaml_path)}"
        )
    return left


def collect_eval_entries(evals_root: Path) -> list[dict[str, Any]]:
    bundles_dir = evals_root / "bundles"
    if not bundles_dir.is_dir():
        raise RouterError(f"{relative_posix(bundles_dir)} is missing")

    entries: list[dict[str, Any]] = []
    for bundle_dir in sorted(path for path in bundles_dir.iterdir() if path.is_dir()):
        eval_md_path = bundle_dir / "EVAL.md"
        eval_yaml_path = bundle_dir / "eval.yaml"

        metadata, _body = parse_frontmatter_markdown(eval_md_path)
        metadata = ensure_mapping(metadata, relative_posix(eval_md_path))
        require_keys(
            metadata,
            (
                "name",
                "category",
                "status",
                "summary",
                "object_under_evaluation",
                "claim_type",
                "baseline_mode",
                "report_format",
                "technique_dependencies",
                "skill_dependencies",
            ),
            relative_posix(eval_md_path),
        )
        manifest = ensure_mapping(load_yaml_file(eval_yaml_path), relative_posix(eval_yaml_path))
        require_keys(
            manifest,
            (
                "name",
                "category",
                "status",
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
            ),
            relative_posix(eval_yaml_path),
        )

        eval_name = ensure_string(metadata["name"], f"{relative_posix(eval_md_path)}.name")
        if eval_name != bundle_dir.name:
            raise RouterError(
                f"{relative_posix(eval_md_path)} frontmatter name '{eval_name}' does not match directory '{bundle_dir.name}'"
            )
        for field_name in (
            "name",
            "category",
            "status",
            "object_under_evaluation",
            "claim_type",
            "baseline_mode",
            "report_format",
        ):
            compare_eval_field(metadata, manifest, field_name, eval_md_path, eval_yaml_path)

        frontmatter_techniques = ensure_string_list(
            metadata["technique_dependencies"],
            f"{relative_posix(eval_md_path)}.technique_dependencies",
        )
        manifest_technique_items = ensure_list(
            manifest["technique_dependencies"],
            f"{relative_posix(eval_yaml_path)}.technique_dependencies",
        )
        manifest_techniques: list[str] = []
        for index, item in enumerate(manifest_technique_items):
            location = f"{relative_posix(eval_yaml_path)}.technique_dependencies[{index}]"
            dependency = ensure_mapping(item, location)
            require_keys(dependency, ("id", "repo", "path"), location)
            dependency_id = ensure_string(dependency["id"], f"{location}.id")
            manifest_techniques.append(dependency_id)
            repo_name = normalize_repo_name(ensure_string(dependency["repo"], f"{location}.repo"))
            if repo_name != "aoa-techniques":
                raise RouterError(f"{location}.repo must resolve to aoa-techniques")
            raw_path = ensure_string(dependency["path"], f"{location}.path")
            if is_pending_technique_id(dependency_id):
                if raw_path != "TBD":
                    ensure_repo_relative_path(raw_path, f"{location}.path")
            else:
                ensure_repo_relative_path(raw_path, f"{location}.path")

        if frontmatter_techniques != manifest_techniques:
            raise RouterError(
                f"{relative_posix(eval_md_path)} technique_dependencies do not match {relative_posix(eval_yaml_path)}"
            )

        frontmatter_skills = ensure_string_list(
            metadata["skill_dependencies"],
            f"{relative_posix(eval_md_path)}.skill_dependencies",
        )
        manifest_skill_items = ensure_list(
            manifest["skill_dependencies"],
            f"{relative_posix(eval_yaml_path)}.skill_dependencies",
        )
        manifest_skills: list[str] = []
        for index, item in enumerate(manifest_skill_items):
            location = f"{relative_posix(eval_yaml_path)}.skill_dependencies[{index}]"
            dependency = ensure_mapping(item, location)
            require_keys(dependency, ("name", "repo", "path"), location)
            dependency_name = ensure_string(dependency["name"], f"{location}.name")
            manifest_skills.append(dependency_name)
            repo_name = normalize_repo_name(ensure_string(dependency["repo"], f"{location}.repo"))
            if repo_name != "aoa-skills":
                raise RouterError(f"{location}.repo must resolve to aoa-skills")
            ensure_repo_relative_path(dependency["path"], f"{location}.path")

        if frontmatter_skills != manifest_skills:
            raise RouterError(
                f"{relative_posix(eval_md_path)} skill_dependencies do not match {relative_posix(eval_yaml_path)}"
            )

        entries.append(
            {
                "kind": "eval",
                "id": eval_name,
                "name": eval_name,
                "repo": "aoa-evals",
                "path": eval_md_path.relative_to(evals_root).as_posix(),
                "status": ensure_string(metadata["status"], f"{relative_posix(eval_md_path)}.status"),
                "summary": ensure_string(metadata["summary"], f"{relative_posix(eval_md_path)}.summary"),
                "source_type": HYBRID_SOURCE_TYPE,
                "attributes": {
                    "category": ensure_string(
                        metadata["category"], f"{relative_posix(eval_md_path)}.category"
                    ),
                    "object_under_evaluation": ensure_string(
                        metadata["object_under_evaluation"],
                        f"{relative_posix(eval_md_path)}.object_under_evaluation",
                    ),
                    "claim_type": ensure_string(
                        metadata["claim_type"], f"{relative_posix(eval_md_path)}.claim_type"
                    ),
                    "baseline_mode": ensure_string(
                        metadata["baseline_mode"],
                        f"{relative_posix(eval_md_path)}.baseline_mode",
                    ),
                    "verdict_shape": ensure_string(
                        manifest["verdict_shape"], f"{relative_posix(eval_yaml_path)}.verdict_shape"
                    ),
                    "review_required": ensure_bool(
                        manifest["review_required"],
                        f"{relative_posix(eval_yaml_path)}.review_required",
                    ),
                    "validation_strength": ensure_string(
                        manifest["validation_strength"],
                        f"{relative_posix(eval_yaml_path)}.validation_strength",
                    ),
                    "export_ready": ensure_bool(
                        manifest["export_ready"], f"{relative_posix(eval_yaml_path)}.export_ready"
                    ),
                    "technique_dependencies": frontmatter_techniques,
                    "skill_dependencies": frontmatter_skills,
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
