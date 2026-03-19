from __future__ import annotations

import json
from pathlib import Path

import build_router
import validate_router


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


def build_fixture_generated(tmp_path: Path) -> Path:
    generated_dir = tmp_path / "generated"
    outputs = build_router.build_outputs(
        FIXTURES_ROOT / "aoa-techniques",
        FIXTURES_ROOT / "aoa-skills",
        FIXTURES_ROOT / "aoa-evals",
        FIXTURES_ROOT / "aoa-memo",
    )
    for filename, payload in outputs.items():
        write_json(generated_dir / filename, payload)
    return generated_dir


def test_validate_generated_outputs_accepts_fixture_build(tmp_path: Path) -> None:
    generated_dir = build_fixture_generated(tmp_path)
    issues = validate_router.validate_generated_outputs(generated_dir)
    assert issues == []


def test_validate_generated_outputs_rejects_duplicate_registry_entry(tmp_path: Path) -> None:
    generated_dir = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["entries"].append(dict(payload["entries"][0]))
    write_json(registry_path, payload)

    issues = validate_router.validate_generated_outputs(generated_dir)
    assert any("duplicate registry entry" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_unresolved_skill_dependency(tmp_path: Path) -> None:
    generated_dir = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    for entry in payload["entries"]:
        if entry["kind"] == "eval" and entry["id"] == "aoa-bounded-change-quality":
            entry["attributes"]["skill_dependencies"] = ["aoa-missing-skill"]
            break
    write_json(registry_path, payload)

    issues = validate_router.validate_generated_outputs(generated_dir)
    assert any("unresolved skill dependency 'aoa-missing-skill'" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_broken_repo_name(tmp_path: Path) -> None:
    generated_dir = build_fixture_generated(tmp_path)
    router_path = generated_dir / "aoa_router.min.json"
    payload = json.loads(router_path.read_text(encoding="utf-8"))
    payload["entries"][0]["repo"] = "github.com/8Dionysus/aoa-techniques"
    write_json(router_path, payload)

    issues = validate_router.validate_generated_outputs(generated_dir)
    assert any("schema violation" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_invalid_recommended_paths(tmp_path: Path) -> None:
    generated_dir = build_fixture_generated(tmp_path)
    recommended_path = generated_dir / "recommended_paths.min.json"
    payload = json.loads(recommended_path.read_text(encoding="utf-8"))
    payload["entries"][0]["downstream"].append(
        {"kind": payload["entries"][0]["kind"], "id": "AOA-T-0002", "relation": "requires"}
    )
    write_json(recommended_path, payload)

    issues = validate_router.validate_generated_outputs(generated_dir)
    assert any("same-kind hops are not allowed" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_memo_objects_in_v0_1(tmp_path: Path) -> None:
    generated_dir = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["entries"].append(
        {
            "kind": "memo",
            "id": "memo-001",
            "name": "memo-001",
            "repo": "aoa-memo",
            "path": "memory/memo-001.md",
            "status": "draft",
            "summary": "future memory object",
            "source_type": "manual",
            "attributes": {},
        }
    )
    write_json(registry_path, payload)

    issues = validate_router.validate_generated_outputs(generated_dir)
    assert any("memo entries are not allowed in v0.1" in issue.message for issue in issues)
