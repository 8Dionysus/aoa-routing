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


def test_collect_skill_entries_reads_generated_catalog() -> None:
    entries = build_router.collect_skill_entries(FIXTURES_ROOT / "aoa-skills")

    assert [entry["id"] for entry in entries] == ["aoa-change-protocol", "aoa-context-scan"]
    assert entries[0]["path"] == "skills/aoa-change-protocol/SKILL.md"
    assert entries[0]["source_type"] == "generated-catalog"
    assert entries[0]["attributes"]["technique_dependencies"] == ["AOA-T-0001", "AOA-T-0002"]


def test_collect_eval_entries_reads_generated_catalog() -> None:
    entries = build_router.collect_eval_entries(FIXTURES_ROOT / "aoa-evals")

    assert [entry["id"] for entry in entries] == [
        "aoa-bounded-change-quality",
        "aoa-context-scan-quality",
    ]
    assert entries[0]["path"] == "bundles/aoa-bounded-change-quality/EVAL.md"
    assert entries[0]["source_type"] == "generated-catalog"
    assert entries[0]["attributes"]["skill_dependencies"] == ["aoa-change-protocol"]


def test_collect_skill_entries_raises_on_missing_generated_catalog(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    (skills_root / "generated" / "skill_catalog.min.json").unlink()

    with pytest.raises(build_router.RouterError, match="skill_catalog.min.json"):
        build_router.collect_skill_entries(skills_root)


def test_collect_eval_entries_raises_on_missing_required_field(tmp_path: Path) -> None:
    evals_root = tmp_path / "aoa-evals"
    shutil.copytree(FIXTURES_ROOT / "aoa-evals", evals_root)
    catalog_path = evals_root / "generated" / "eval_catalog.min.json"
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    del payload["evals"][0]["verdict_shape"]
    write_json(catalog_path, payload)

    with pytest.raises(build_router.RouterError, match="verdict_shape"):
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
    assert {entry["source_type"] for entry in registry["entries"]} == {"generated-catalog"}

    technique_hint = next(hint for hint in hints["hints"] if hint["kind"] == "technique")
    assert technique_hint["actions"]["inspect"] == {
        "enabled": True,
        "surface_file": "generated/technique_capsules.json",
        "match_field": "id",
    }
    assert hints["hints"][-1] == {
        "kind": "memo",
        "enabled": False,
        "source_repo": "aoa-memo",
        "use_when": "reserved for future recall and memory-routing surfaces",
        "actions": {
            "pick": {"enabled": False},
            "inspect": {"enabled": False},
            "expand": {"enabled": False},
            "pair": {"enabled": False},
            "recall": {"enabled": False},
        },
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


def test_build_uses_catalog_only_ingestion_for_skills_and_evals(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    evals_root = tmp_path / "aoa-evals"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    shutil.copytree(FIXTURES_ROOT / "aoa-evals", evals_root)
    shutil.rmtree(skills_root / "skills")
    shutil.rmtree(evals_root / "bundles")

    outputs = build_router.build_outputs(
        FIXTURES_ROOT / "aoa-techniques",
        skills_root,
        evals_root,
        FIXTURES_ROOT / "aoa-memo",
    )

    assert len(outputs["cross_repo_registry.min.json"]["entries"]) == 6


def test_build_allows_pending_technique_dependencies_without_creating_paths(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    catalog_path = skills_root / "generated" / "skill_catalog.min.json"
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    for skill in payload["skills"]:
        if skill["name"] == "aoa-context-scan":
            skill["technique_dependencies"] = ["AOA-T-PENDING-CONTEXT-SCAN"]
            break
    write_json(catalog_path, payload)

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
