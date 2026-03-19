from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import build_router


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


def test_collect_technique_entries_reads_generated_catalog() -> None:
    entries = build_router.collect_technique_entries(FIXTURES_ROOT / "aoa-techniques")

    assert [entry["id"] for entry in entries] == ["AOA-T-0001", "AOA-T-0002"]
    assert entries[0]["kind"] == "technique"
    assert entries[0]["repo"] == "aoa-techniques"
    assert entries[0]["source_type"] == "generated-catalog"
    assert entries[0]["attributes"]["domain"] == "agent-workflows"


def test_collect_skill_entries_raises_on_dependency_mismatch(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    skill_md = skills_root / "skills" / "aoa-change-protocol" / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    skill_md.write_text(text.replace("  - AOA-T-0002\n", ""), encoding="utf-8")

    with pytest.raises(build_router.RouterError, match="technique_dependencies do not match"):
        build_router.collect_skill_entries(skills_root)


def test_collect_eval_entries_raises_on_frontmatter_manifest_mismatch(tmp_path: Path) -> None:
    evals_root = tmp_path / "aoa-evals"
    shutil.copytree(FIXTURES_ROOT / "aoa-evals", evals_root)
    eval_yaml = evals_root / "bundles" / "aoa-bounded-change-quality" / "eval.yaml"
    text = eval_yaml.read_text(encoding="utf-8")
    eval_yaml.write_text(text.replace("baseline_mode: none", "baseline_mode: fixed-baseline"), encoding="utf-8")

    with pytest.raises(build_router.RouterError, match="field 'baseline_mode' does not match"):
        build_router.collect_eval_entries(evals_root)


def test_collect_skill_entries_raises_on_missing_source_file(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    techniques_yaml = skills_root / "skills" / "aoa-change-protocol" / "techniques.yaml"
    techniques_yaml.unlink()

    with pytest.raises(build_router.RouterError, match="techniques.yaml"):
        build_router.collect_skill_entries(skills_root)


def test_collect_eval_entries_rejects_unsupported_repo_reference(tmp_path: Path) -> None:
    evals_root = tmp_path / "aoa-evals"
    shutil.copytree(FIXTURES_ROOT / "aoa-evals", evals_root)
    eval_yaml = evals_root / "bundles" / "aoa-context-scan-quality" / "eval.yaml"
    text = eval_yaml.read_text(encoding="utf-8")
    eval_yaml.write_text(text.replace("repo: aoa-skills", "repo: unsupported-repo"), encoding="utf-8")

    with pytest.raises(build_router.RouterError, match="unsupported repo reference"):
        build_router.collect_eval_entries(evals_root)


def test_build_outputs_from_fixtures() -> None:
    outputs = build_router.build_outputs(
        FIXTURES_ROOT / "aoa-techniques",
        FIXTURES_ROOT / "aoa-skills",
        FIXTURES_ROOT / "aoa-evals",
        FIXTURES_ROOT / "aoa-memo",
    )

    registry = outputs["cross_repo_registry.min.json"]
    router = outputs["aoa_router.min.json"]
    hints = outputs["task_to_surface_hints.json"]
    recommended = outputs["recommended_paths.min.json"]

    assert [entry["kind"] for entry in registry["entries"]] == [
        "technique",
        "technique",
        "skill",
        "skill",
        "eval",
        "eval",
    ]
    assert all(entry["kind"] != "memo" for entry in router["entries"])
    assert hints["hints"][-1] == {
        "kind": "memo",
        "enabled": False,
        "source_repo": "aoa-memo",
        "use_when": "reserved for future recall and memory-routing surfaces",
    }

    by_key = {(entry["kind"], entry["id"]): entry for entry in recommended["entries"]}
    change_skill = by_key[("skill", "aoa-change-protocol")]
    assert change_skill["upstream"] == [
        {"kind": "technique", "id": "AOA-T-0001", "relation": "requires"},
        {"kind": "technique", "id": "AOA-T-0002", "relation": "requires"},
    ]
    context_eval = by_key[("eval", "aoa-context-scan-quality")]
    assert context_eval["upstream"] == [
        {"kind": "technique", "id": "AOA-T-0002", "relation": "requires"},
        {"kind": "skill", "id": "aoa-context-scan", "relation": "requires"},
    ]


def test_build_allows_pending_technique_dependencies_without_creating_paths(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    skill_md = skills_root / "skills" / "aoa-context-scan" / "SKILL.md"
    skill_text = skill_md.read_text(encoding="utf-8")
    skill_md.write_text(skill_text.replace("AOA-T-0002", "AOA-T-PENDING-CONTEXT-SCAN"), encoding="utf-8")
    techniques_yaml = skills_root / "skills" / "aoa-context-scan" / "techniques.yaml"
    techniques_text = techniques_yaml.read_text(encoding="utf-8")
    techniques_text = techniques_text.replace("id: AOA-T-0002", "id: AOA-T-PENDING-CONTEXT-SCAN")
    techniques_text = techniques_text.replace(
        "path: techniques/docs/context-scan/TECHNIQUE.md",
        "path: TBD",
    )
    techniques_yaml.write_text(techniques_text, encoding="utf-8")

    outputs = build_router.build_outputs(
        FIXTURES_ROOT / "aoa-techniques",
        skills_root,
        FIXTURES_ROOT / "aoa-evals",
        FIXTURES_ROOT / "aoa-memo",
    )

    registry_entries = outputs["cross_repo_registry.min.json"]["entries"]
    skill_entry = next(entry for entry in registry_entries if entry["id"] == "aoa-context-scan")
    assert skill_entry["attributes"]["technique_dependencies"] == ["AOA-T-PENDING-CONTEXT-SCAN"]

    by_key = {
        (entry["kind"], entry["id"]): entry
        for entry in outputs["recommended_paths.min.json"]["entries"]
    }
    assert by_key[("skill", "aoa-context-scan")]["upstream"] == []


def test_build_is_deterministic_on_repeated_runs(tmp_path: Path) -> None:
    generated_dir = tmp_path / "generated"
    outputs_a = build_router.build_outputs(
        FIXTURES_ROOT / "aoa-techniques",
        FIXTURES_ROOT / "aoa-skills",
        FIXTURES_ROOT / "aoa-evals",
        FIXTURES_ROOT / "aoa-memo",
    )
    for filename, payload in outputs_a.items():
        write_json(generated_dir / filename, payload)
    snapshot_a = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(generated_dir.iterdir())
    }

    outputs_b = build_router.build_outputs(
        FIXTURES_ROOT / "aoa-techniques",
        FIXTURES_ROOT / "aoa-skills",
        FIXTURES_ROOT / "aoa-evals",
        FIXTURES_ROOT / "aoa-memo",
    )
    for filename, payload in outputs_b.items():
        write_json(generated_dir / filename, payload)
    snapshot_b = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(generated_dir.iterdir())
    }

    assert snapshot_a == snapshot_b
