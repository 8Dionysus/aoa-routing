#!/usr/bin/env python3
"""Validate wave-9 two-stage skill-routing artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROFILE = "aoa-routing-wave-9-two-stage-skill-router"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def resolve_generated_dir(path: Path) -> Path:
    if (path / "two_stage_skill_entrypoints.json").exists():
        return path
    candidate = path / "generated"
    if (candidate / "two_stage_skill_entrypoints.json").exists():
        return candidate
    return path


def validate_outputs(routing_root: Path, skills_root: Path) -> list[tuple[str, str]]:
    generated_dir = resolve_generated_dir(routing_root)
    issues: list[tuple[str, str]] = []
    entrypoints = load_json(generated_dir / "two_stage_skill_entrypoints.json")
    prompt_blocks = load_json(generated_dir / "two_stage_router_prompt_blocks.json")
    tool_schemas = load_json(generated_dir / "two_stage_router_tool_schemas.json")
    examples = load_json(generated_dir / "two_stage_router_examples.json")
    manifest = load_json(generated_dir / "two_stage_router_manifest.json")
    eval_cases = load_jsonl(generated_dir / "two_stage_router_eval_cases.jsonl")
    tiny_capsules = load_json(skills_root / "generated" / "tiny_router_capsules.min.json")

    for label, doc in {
        "two_stage_skill_entrypoints.json": entrypoints,
        "two_stage_router_prompt_blocks.json": prompt_blocks,
        "two_stage_router_tool_schemas.json": tool_schemas,
        "two_stage_router_examples.json": examples,
        "two_stage_router_manifest.json": manifest,
    }.items():
        if doc.get("profile") != PROFILE:
            issues.append((label, f"profile must be {PROFILE!r}"))

    skill_names = {entry["name"] for entry in tiny_capsules.get("skills", [])}
    top_k_default = entrypoints.get("stage_1", {}).get("top_k_default")
    if entrypoints.get("stage_1", {}).get("activation_policy") != "never-activate":
        issues.append(("two_stage_skill_entrypoints.json", "stage_1 activation_policy must stay never-activate"))
    if entrypoints.get("stage_2", {}).get("decision_modes") != [
        "activate-candidate",
        "manual-invocation-required",
        "no-skill",
    ]:
        issues.append(("two_stage_skill_entrypoints.json", "stage_2 decision_modes mismatch"))
    if entrypoints.get("routing_refs", {}).get("tiny_model_entrypoints") != "generated/tiny_model_entrypoints.json":
        issues.append(("two_stage_skill_entrypoints.json", "routing_refs tiny_model_entrypoints mismatch"))

    if len(tool_schemas.get("tools", [])) != 3:
        issues.append(("two_stage_router_tool_schemas.json", "expected exactly 3 tool schemas"))
    if "tiny_preselector_system" not in prompt_blocks or "main_model_decision_system" not in prompt_blocks:
        issues.append(("two_stage_router_prompt_blocks.json", "missing required prompt blocks"))

    for example in examples.get("examples", []):
        shortlist = example.get("preselect_result", {}).get("shortlist", [])
        if top_k_default is not None and len(shortlist) > top_k_default:
            issues.append(("two_stage_router_examples.json", "example shortlist exceeds configured top_k"))
        for item in shortlist:
            if item.get("name") not in skill_names:
                issues.append(("two_stage_router_examples.json", f"unknown skill in shortlist: {item.get('name')!r}"))

    for case in eval_cases:
        for name in case.get("expected_shortlist_includes", []):
            if name not in skill_names:
                issues.append(("two_stage_router_eval_cases.jsonl", f"unknown expected skill {name!r}"))
        top1 = case.get("expected_top1")
        if top1 is not None and top1 not in skill_names:
            issues.append(("two_stage_router_eval_cases.jsonl", f"unknown expected_top1 {top1!r}"))
        top1_not = case.get("expected_top1_not")
        if top1_not is not None and top1_not not in skill_names:
            issues.append(("two_stage_router_eval_cases.jsonl", f"unknown expected_top1_not {top1_not!r}"))

    if manifest.get("skill_count") != len(skill_names):
        issues.append(("two_stage_router_manifest.json", "skill_count mismatch"))
    if manifest.get("example_count") != len(examples.get("examples", [])):
        issues.append(("two_stage_router_manifest.json", "example_count mismatch"))
    if manifest.get("eval_case_count") != len(eval_cases):
        issues.append(("two_stage_router_manifest.json", "eval_case_count mismatch"))
    if manifest.get("integration_mode") != "adjacent-seam":
        issues.append(("two_stage_router_manifest.json", "integration_mode mismatch"))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate wave-9 two-stage skill-routing artifacts.")
    parser.add_argument("--routing-root", default=".", type=Path, help="aoa-routing repository root.")
    parser.add_argument("--skills-root", default=Path("..") / "aoa-skills", type=Path, help="aoa-skills repository root.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print output JSON.")
    args = parser.parse_args()

    issues = validate_outputs(args.routing_root.resolve(), args.skills_root.resolve())
    payload = {
        "status": "ok" if not issues else "fail",
        "issues": [{"location": location, "message": message} for location, message in issues],
    }
    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload))
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
