from __future__ import annotations

import json
import shutil
from pathlib import Path

import build_router
import validate_router


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


def copy_fixture_roots(tmp_path: Path) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for repo_name in ("aoa-techniques", "aoa-skills", "aoa-evals"):
        target = tmp_path / repo_name
        shutil.copytree(FIXTURES_ROOT / repo_name, target)
        roots[repo_name] = target
    roots["aoa-memo"] = tmp_path / "aoa-memo"
    roots["aoa-memo"].mkdir(parents=True, exist_ok=True)
    return roots


def build_fixture_generated(tmp_path: Path) -> tuple[Path, dict[str, Path]]:
    roots = copy_fixture_roots(tmp_path)
    generated_dir = tmp_path / "generated"
    outputs = build_router.build_outputs(
        roots["aoa-techniques"],
        roots["aoa-skills"],
        roots["aoa-evals"],
        roots["aoa-memo"],
    )
    for filename, payload in outputs.items():
        write_json(generated_dir / filename, payload)
    return generated_dir, roots


def validate_fixture_generated(generated_dir: Path, roots: dict[str, Path]) -> list[validate_router.ValidationIssue]:
    return validate_router.validate_generated_outputs(
        generated_dir,
        roots["aoa-techniques"],
        roots["aoa-skills"],
        roots["aoa-evals"],
        roots["aoa-memo"],
    )


def test_validate_generated_outputs_accepts_fixture_build(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    issues = validate_fixture_generated(generated_dir, roots)
    assert issues == []


def test_validate_generated_outputs_rejects_missing_registry_version_key_via_schema(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    del payload["registry_version"]
    write_json(registry_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and "registry_version" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_duplicate_registry_entry(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["entries"].append(dict(payload["entries"][0]))
    write_json(registry_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("duplicate registry entry" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_unresolved_skill_dependency(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    for entry in payload["entries"]:
        if entry["kind"] == "eval" and entry["id"] == "aoa-bounded-change-quality":
            entry["attributes"]["skill_dependencies"] = ["aoa-missing-skill"]
            break
    write_json(registry_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("unresolved skill dependency 'aoa-missing-skill'" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_non_generated_source_type(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["entries"][0]["source_type"] = "markdown-frontmatter+manifest"
    write_json(registry_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("source_type 'generated-catalog'" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_broken_repo_name(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    router_path = generated_dir / "aoa_router.min.json"
    payload = json.loads(router_path.read_text(encoding="utf-8"))
    payload["entries"][0]["repo"] = "github.com/8Dionysus/aoa-techniques"
    write_json(router_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("schema violation" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_router_projection_shape_drift_via_schema(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    router_path = generated_dir / "aoa_router.min.json"
    payload = json.loads(router_path.read_text(encoding="utf-8"))
    payload["entries"][0]["source_type"] = "generated-catalog"
    write_json(router_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and "source_type" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_registry_entry_missing_kind_without_crashing(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    del payload["entries"][0]["kind"]
    write_json(registry_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("schema violation" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_missing_attributes_without_crashing(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    for entry in payload["entries"]:
        if entry["kind"] == "skill":
            del entry["attributes"]
            break
    write_json(registry_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("attributes must be an object" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_invalid_dependency_attributes_without_crashing(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    for entry in payload["entries"]:
        if entry["kind"] == "eval":
            entry["attributes"]["technique_dependencies"] = "AOA-T-0001"
            break
    write_json(registry_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("technique_dependencies must be a list" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_malformed_inspect_action_shape_via_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    del payload["hints"][0]["actions"]["inspect"]["match_field"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        ("schema violation" in issue.message and "actions.inspect" in issue.message)
        or "must define match_field" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_malformed_expand_action_shape_via_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    del payload["hints"][0]["actions"]["expand"]["supported_sections"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        ("schema violation" in issue.message and "actions.expand" in issue.message)
        or "must define supported_sections" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_enabled_pair_or_recall_actions_via_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    payload["hints"][0]["actions"]["pair"]["enabled"] = True
    payload["hints"][1]["actions"]["recall"]["enabled"] = True
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and ".actions.pair.enabled" in issue.message
        for issue in issues
    )
    assert any(
        "schema violation" in issue.message and ".actions.recall.enabled" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_invalid_recommended_paths(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    recommended_path = generated_dir / "recommended_paths.min.json"
    payload = json.loads(recommended_path.read_text(encoding="utf-8"))
    payload["entries"][0]["downstream"].append(
        {"kind": payload["entries"][0]["kind"], "id": "AOA-T-0002", "relation": "requires"}
    )
    write_json(recommended_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("same-kind hops are not allowed" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_malformed_recommended_hop_via_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    recommended_path = generated_dir / "recommended_paths.min.json"
    payload = json.loads(recommended_path.read_text(encoding="utf-8"))
    del payload["entries"][0]["downstream"][0]["relation"]
    write_json(recommended_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and "relation" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_missing_inspect_target(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    capsules_path = roots["aoa-skills"] / "generated" / "skill_capsules.json"
    payload = json.loads(capsules_path.read_text(encoding="utf-8"))
    payload["skills"] = [
        entry for entry in payload["skills"] if entry["name"] != "aoa-context-scan"
    ]
    write_json(capsules_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("inspect surface is missing skill match 'aoa-context-scan'" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_missing_expand_target(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    sections_path = roots["aoa-skills"] / "generated" / "skill_sections.full.json"
    payload = json.loads(sections_path.read_text(encoding="utf-8"))
    payload["skills"] = [
        entry for entry in payload["skills"] if entry["name"] != "aoa-context-scan"
    ]
    write_json(sections_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("expand surface is missing skill match 'aoa-context-scan'" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_section_payload_leakage(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    router_path = generated_dir / "aoa_router.min.json"
    payload = json.loads(router_path.read_text(encoding="utf-8"))
    payload["entries"][0]["content_markdown"] = "copied source text"
    write_json(router_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must not copy source-owned payload key 'content_markdown'" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_capsule_payload_leakage(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    router_path = generated_dir / "aoa_router.min.json"
    payload = json.loads(router_path.read_text(encoding="utf-8"))
    payload["entries"][0]["one_line_intent"] = "copied capsule text"
    write_json(router_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must not copy source-owned payload key 'one_line_intent'" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_memo_objects_in_v0_1(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
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

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("memo entries are not allowed in v0.1" in issue.message for issue in issues)
