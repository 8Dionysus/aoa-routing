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
    for repo_name in ("aoa-techniques", "aoa-skills", "aoa-evals", "aoa-memo", "aoa-agents"):
        target = tmp_path / repo_name
        shutil.copytree(FIXTURES_ROOT / repo_name, target)
        roots[repo_name] = target
    return roots


def build_fixture_generated(tmp_path: Path) -> tuple[Path, dict[str, Path]]:
    roots = copy_fixture_roots(tmp_path)
    generated_dir = tmp_path / "generated"
    outputs = build_router.build_outputs(
        roots["aoa-techniques"],
        roots["aoa-skills"],
        roots["aoa-evals"],
        roots["aoa-memo"],
        roots["aoa-agents"],
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
        roots["aoa-agents"],
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


def test_validate_generated_outputs_rejects_stale_registry_and_router_against_rebuild(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    router_path = generated_dir / "aoa_router.min.json"

    registry_payload = json.loads(registry_path.read_text(encoding="utf-8"))
    router_payload = json.loads(router_path.read_text(encoding="utf-8"))
    registry_payload["entries"][0]["summary"] = "stale routing snapshot"
    router_payload["entries"][0]["summary"] = "stale routing snapshot"
    write_json(registry_path, registry_payload)
    write_json(router_path, router_payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "cross_repo_registry.min.json"
        and "canonical rebuild from current sibling catalogs" in issue.message
        for issue in issues
    )
    assert any(
        issue.location == "aoa_router.min.json"
        and "canonical rebuild from current sibling catalogs" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_broken_repo_name(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    router_path = generated_dir / "aoa_router.min.json"
    payload = json.loads(router_path.read_text(encoding="utf-8"))
    payload["entries"][0]["repo"] = "github.com/8Dionysus/aoa-techniques"
    write_json(router_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("schema violation" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_canonical_repo_mismatch_even_if_consistent(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    router_path = generated_dir / "aoa_router.min.json"

    registry_payload = json.loads(registry_path.read_text(encoding="utf-8"))
    router_payload = json.loads(router_path.read_text(encoding="utf-8"))
    registry_payload["entries"][0]["repo"] = "aoa-skills"
    router_payload["entries"][0]["repo"] = "aoa-skills"
    write_json(registry_path, registry_payload)
    write_json(router_path, router_payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("canonical repo 'aoa-techniques'" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_absolute_path_even_if_consistent(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = generated_dir / "cross_repo_registry.min.json"
    router_path = generated_dir / "aoa_router.min.json"

    registry_payload = json.loads(registry_path.read_text(encoding="utf-8"))
    router_payload = json.loads(router_path.read_text(encoding="utf-8"))
    registry_payload["entries"][0]["path"] = "C:/secret/TECHNIQUE.md"
    router_payload["entries"][0]["path"] = "C:/secret/TECHNIQUE.md"
    write_json(registry_path, registry_payload)
    write_json(router_path, router_payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("must be repo-relative, not absolute" in issue.message for issue in issues)


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


def test_validate_generated_outputs_reports_missing_model_tier_registry_without_crashing(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    (roots["aoa-agents"] / "generated" / "model_tier_registry.json").unlink()

    issues = validate_fixture_generated(generated_dir, roots)

    assert any(
        issue.location == "task_to_tier_hints.json"
        and "could not rebuild task_to_tier_hints.json from aoa-agents" in issue.message
        for issue in issues
    )
    assert any(
        issue.location == "task_to_tier_hints.json"
        and "is missing" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_missing_hint_enabled_without_crashing(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    del payload["hints"][0]["enabled"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("schema violation" in issue.message and "enabled" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_malformed_tier_hint_shape_via_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tier_hints_path = generated_dir / "task_to_tier_hints.json"
    payload = json.loads(tier_hints_path.read_text(encoding="utf-8"))
    del payload["hints"][0]["preferred_tier"]
    write_json(tier_hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and "preferred_tier" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_unknown_tier_reference(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tier_hints_path = generated_dir / "task_to_tier_hints.json"
    payload = json.loads(tier_hints_path.read_text(encoding="utf-8"))
    payload["hints"][0]["preferred_tier"] = "ghost-tier"
    write_json(tier_hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "preferred_tier references unknown tier 'ghost-tier'" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_agents_registry_drift_for_tier_hints(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    registry_path = roots["aoa-agents"] / "generated" / "model_tier_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["model_tiers"][0]["artifact_requirement"] = "triage_packet"
    write_json(registry_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "task_to_tier_hints.json"
        and "canonical rebuild from current sibling catalogs" in issue.message
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


def test_validate_generated_outputs_rejects_malformed_enabled_pair_action_via_schema(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    del payload["hints"][0]["actions"]["pair"]["surface_repo"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        ("schema violation" in issue.message and "actions.pair" in issue.message)
        or "must define surface_file" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_malformed_enabled_recall_action_via_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    del memo_hint["actions"]["recall"]["contracts_by_mode"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        ("schema violation" in issue.message and "actions.recall" in issue.message)
        or "must define contracts_by_mode" in issue.message
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


def test_validate_generated_outputs_rejects_invalid_kag_relation_hints(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    relation_hints_path = generated_dir / "kag_source_lift_relation_hints.min.json"
    payload = json.loads(relation_hints_path.read_text(encoding="utf-8"))
    payload["entries"].append(
        {
            "kind": "technique",
            "id": "AOA-T-0018",
            "name": "markdown-technique-section-lift",
            "summary": "Lift stable technique markdown sections into derived section-level units while keeping the bundle markdown authoritative.",
            "relations": [{"type": "complements", "target": "AOA-T-9999"}],
        }
    )
    write_json(relation_hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "kag_source_lift_relation_hints.min.json does not match the live direct relation surface"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_invalid_pairing_hints(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    pairing_path = generated_dir / "pairing_hints.min.json"
    payload = json.loads(pairing_path.read_text(encoding="utf-8"))
    payload["entries"][0]["pairs"].append(
        {"kind": payload["entries"][0]["kind"], "id": "AOA-T-0002", "relation": "requires"}
    )
    write_json(pairing_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "same-kind pairing must stay within the KAG/source-lift family" in issue.message
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


def test_validate_generated_outputs_rejects_invalid_recommended_memo_hop_kind(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    recommended_path = generated_dir / "recommended_paths.min.json"
    payload = json.loads(recommended_path.read_text(encoding="utf-8"))
    payload["entries"][0]["downstream"].append(
        {"kind": "memo", "id": "AOA-M-0001", "relation": "requires"}
    )
    write_json(recommended_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        ("schema violation" in issue.message and "downstream[1].kind" in issue.message)
        or "hop kind must be technique, skill, or eval" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_missing_recall_contract_target(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    contract_path = roots["aoa-memo"] / "examples" / "recall_contract.router.semantic.json"
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    payload["expand_surface"] = "generated/memory_capsules.json"
    write_json(contract_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "recall contract expand_surface must match the memo expand surface hint" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tiny_model_entrypoint_missing_surface(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"
    payload = json.loads(tiny_model_path.read_text(encoding="utf-8"))
    payload["queries"][0]["target_surface"] = "generated/missing-router-surface.json"
    write_json(tiny_model_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "aoa-routing/generated/missing-router-surface.json"
        and "is missing" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_duplicate_tiny_model_starter_name(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"
    payload = json.loads(tiny_model_path.read_text(encoding="utf-8"))
    payload["starters"][1]["name"] = payload["starters"][0]["name"]
    write_json(tiny_model_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any("starter names must be unique" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_tiny_model_starter_missing_target(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"
    payload = json.loads(tiny_model_path.read_text(encoding="utf-8"))
    payload["starters"][1]["target_value"] = "ghost-kind"
    write_json(tiny_model_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "starter 'technique-root' target 'ghost-kind' was not found" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tiny_model_recall_starter_unsupported_mode(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"
    payload = json.loads(tiny_model_path.read_text(encoding="utf-8"))
    recall_starter = next(starter for starter in payload["starters"] if starter["verb"] == "recall")
    recall_starter["recall_mode"] = "episodic"
    write_json(tiny_model_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "uses unsupported recall mode 'episodic'" in issue.message
        for issue in issues
    )
