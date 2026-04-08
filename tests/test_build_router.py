from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import build_router


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"
FIXTURE_REPO_NAMES = (
    "aoa-techniques",
    "aoa-skills",
    "aoa-evals",
    "aoa-memo",
    "aoa-stats",
    "aoa-sdk",
    "aoa-agents",
    "Agents-of-Abyss",
    "aoa-playbooks",
    "aoa-kag",
    "Tree-of-Sophia",
    "Dionysus",
    "8Dionysus",
    "abyss-stack",
)
KAG_SOURCE_LIFT_TECHNIQUE_IDS = [
    "AOA-T-0018",
    "AOA-T-0019",
    "AOA-T-0020",
    "AOA-T-0021",
    "AOA-T-0022",
]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


def write_output(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".jsonl":
        rows = payload if isinstance(payload, list) else [payload]
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
        return
    write_json(path, payload)


def build_fixture_outputs(
    *,
    techniques_root: Path = FIXTURES_ROOT / "aoa-techniques",
    skills_root: Path = FIXTURES_ROOT / "aoa-skills",
    evals_root: Path = FIXTURES_ROOT / "aoa-evals",
    memo_root: Path = FIXTURES_ROOT / "aoa-memo",
    stats_root: Path = FIXTURES_ROOT / "aoa-stats",
    sdk_root: Path = FIXTURES_ROOT / "aoa-sdk",
    agents_root: Path = FIXTURES_ROOT / "aoa-agents",
    aoa_root: Path = FIXTURES_ROOT / "Agents-of-Abyss",
    playbooks_root: Path = FIXTURES_ROOT / "aoa-playbooks",
    kag_root: Path = FIXTURES_ROOT / "aoa-kag",
    tos_root: Path = FIXTURES_ROOT / "Tree-of-Sophia",
    seed_root: Path = FIXTURES_ROOT / "Dionysus",
    profile_root: Path = FIXTURES_ROOT / "8Dionysus",
    abyss_stack_root: Path = FIXTURES_ROOT / "abyss-stack",
) -> dict[str, dict[str, object]]:
    return build_router.build_outputs(
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        stats_root,
        agents_root,
        aoa_root,
        playbooks_root,
        kag_root,
        tos_root,
        sdk_root,
        seed_root,
        profile_root,
        abyss_stack_root,
    )


def build_kag_source_lift_technique_entries() -> list[dict[str, object]]:
    return [
        {
            "id": "AOA-T-0018",
            "name": "markdown-technique-section-lift",
            "domain": "docs",
            "status": "promoted",
            "summary": "Lift stable technique markdown sections into derived section-level units while keeping the bundle markdown authoritative.",
            "maturity_score": 3,
            "rigor_level": "bounded",
            "reversibility": "easy",
            "review_required": True,
            "validation_strength": "source_backed",
            "export_ready": True,
            "technique_path": "techniques/docs/markdown-technique-section-lift/TECHNIQUE.md",
            "relations": [{"type": "complements", "target": "AOA-T-0019"}],
        },
        {
            "id": "AOA-T-0019",
            "name": "frontmatter-metadata-spine",
            "domain": "docs",
            "status": "canonical",
            "summary": "Treat bounded frontmatter and derived catalog outputs as a metadata spine for bundle routing without replacing markdown meaning.",
            "maturity_score": 5,
            "rigor_level": "bounded",
            "reversibility": "easy",
            "review_required": True,
            "validation_strength": "cross_context",
            "export_ready": True,
            "technique_path": "techniques/docs/frontmatter-metadata-spine/TECHNIQUE.md",
            "relations": [
                {"type": "complements", "target": "AOA-T-0018"},
                {"type": "used_together_for", "target": "AOA-T-0020"},
                {"type": "used_together_for", "target": "AOA-T-0021"},
            ],
        },
        {
            "id": "AOA-T-0020",
            "name": "evidence-note-provenance-lift",
            "domain": "docs",
            "status": "promoted",
            "summary": "Use typed evidence note kinds and note paths as bounded provenance handles in derived manifests without flattening them into a note graph.",
            "maturity_score": 3,
            "rigor_level": "bounded",
            "reversibility": "easy",
            "review_required": True,
            "validation_strength": "source_backed",
            "export_ready": True,
            "technique_path": "techniques/docs/evidence-note-provenance-lift/TECHNIQUE.md",
            "relations": [{"type": "requires", "target": "AOA-T-0019"}],
        },
        {
            "id": "AOA-T-0021",
            "name": "bounded-relation-lift-for-kag",
            "domain": "docs",
            "status": "promoted",
            "summary": "Lift small typed direct relations into bounded edge hints for derived consumers without turning them into graph semantics.",
            "maturity_score": 3,
            "rigor_level": "bounded",
            "reversibility": "easy",
            "review_required": True,
            "validation_strength": "source_backed",
            "export_ready": True,
            "technique_path": "techniques/docs/bounded-relation-lift-for-kag/TECHNIQUE.md",
            "relations": [{"type": "requires", "target": "AOA-T-0019"}],
        },
        {
            "id": "AOA-T-0022",
            "name": "risk-and-negative-effect-lift",
            "domain": "docs",
            "status": "promoted",
            "summary": "Lift richer `Risks` language into bounded caution-oriented lookup and reuse without turning caution into metadata or scoring.",
            "maturity_score": 3,
            "rigor_level": "bounded",
            "reversibility": "easy",
            "review_required": True,
            "validation_strength": "source_backed",
            "export_ready": True,
            "technique_path": "techniques/docs/risk-and-negative-effect-lift/TECHNIQUE.md",
            "relations": [{"type": "complements", "target": "AOA-T-0018"}],
        },
    ]


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


def test_collect_memo_entries_reads_generated_catalog() -> None:
    entries = build_router.collect_memo_entries(FIXTURES_ROOT / "aoa-memo")

    assert [entry["id"] for entry in entries] == ["AOA-M-0001", "AOA-M-0002"]
    assert entries[0]["kind"] == "memo"
    assert entries[0]["repo"] == "aoa-memo"
    assert entries[0]["path"] == "CHARTER.md"
    assert entries[0]["source_type"] == "generated-catalog"
    assert entries[0]["attributes"]["recall_modes"] == ["semantic", "source_route"]
    assert entries[0]["attributes"]["inspect_surface"] == "generated/memory_catalog.min.json"


def test_collect_skill_entries_raises_on_missing_generated_catalog(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    (skills_root / "generated" / "skill_catalog.min.json").unlink()

    with pytest.raises(build_router.RouterError, match="skill_catalog.min.json"):
        build_router.collect_skill_entries(skills_root)


def test_build_outputs_rejects_missing_live_quest_catalog_surface(tmp_path: Path) -> None:
    roots = {}
    for repo_name in FIXTURE_REPO_NAMES:
        target = tmp_path / repo_name
        shutil.copytree(FIXTURES_ROOT / repo_name, target)
        roots[repo_name] = target
    (roots["aoa-techniques"] / "generated" / "quest_catalog.min.json").unlink()

    with pytest.raises(build_router.RouterError, match="quest_catalog.min.json"):
        build_router.build_outputs(
            roots["aoa-techniques"],
            roots["aoa-skills"],
            roots["aoa-evals"],
            roots["aoa-memo"],
            roots["aoa-stats"],
            roots["aoa-agents"],
            roots["Agents-of-Abyss"],
            roots["aoa-playbooks"],
            roots["aoa-kag"],
            roots["Tree-of-Sophia"],
            roots["aoa-sdk"],
            roots["Dionysus"],
            roots["8Dionysus"],
            roots["abyss-stack"],
        )


def test_build_outputs_rejects_missing_live_quest_dispatch_surface(tmp_path: Path) -> None:
    roots = {}
    for repo_name in FIXTURE_REPO_NAMES:
        target = tmp_path / repo_name
        shutil.copytree(FIXTURES_ROOT / repo_name, target)
        roots[repo_name] = target
    (roots["aoa-skills"] / "generated" / "quest_dispatch.min.json").unlink()

    with pytest.raises(build_router.RouterError, match="quest_dispatch.min.json"):
        build_router.build_outputs(
            roots["aoa-techniques"],
            roots["aoa-skills"],
            roots["aoa-evals"],
            roots["aoa-memo"],
            roots["aoa-stats"],
            roots["aoa-agents"],
            roots["Agents-of-Abyss"],
            roots["aoa-playbooks"],
            roots["aoa-kag"],
            roots["Tree-of-Sophia"],
            roots["aoa-sdk"],
            roots["Dionysus"],
            roots["8Dionysus"],
            roots["abyss-stack"],
        )


def test_collect_eval_entries_raises_on_missing_required_field(tmp_path: Path) -> None:
    evals_root = tmp_path / "aoa-evals"
    shutil.copytree(FIXTURES_ROOT / "aoa-evals", evals_root)
    catalog_path = evals_root / "generated" / "eval_catalog.min.json"
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    del payload["evals"][0]["verdict_shape"]
    write_json(catalog_path, payload)

    with pytest.raises(build_router.RouterError, match="verdict_shape"):
        build_router.collect_eval_entries(evals_root)


def test_collect_skill_entries_rejects_parent_directory_skill_path(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    catalog_path = skills_root / "generated" / "skill_catalog.min.json"
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    payload["skills"][0]["skill_path"] = "../secret.md"
    write_json(catalog_path, payload)

    with pytest.raises(build_router.RouterError, match="must not traverse outside the repository root"):
        build_router.collect_skill_entries(skills_root)


def test_collect_eval_entries_rejects_parent_directory_eval_path(tmp_path: Path) -> None:
    evals_root = tmp_path / "aoa-evals"
    shutil.copytree(FIXTURES_ROOT / "aoa-evals", evals_root)
    catalog_path = evals_root / "generated" / "eval_catalog.min.json"
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    payload["evals"][0]["eval_path"] = "../secret.md"
    write_json(catalog_path, payload)

    with pytest.raises(build_router.RouterError, match="must not traverse outside the repository root"):
        build_router.collect_eval_entries(evals_root)


def test_build_outputs_from_fixtures() -> None:
    outputs = build_fixture_outputs()

    registry = outputs["cross_repo_registry.min.json"]
    router = outputs["aoa_router.min.json"]
    hints = outputs["task_to_surface_hints.json"]
    tier_hints = outputs["task_to_tier_hints.json"]
    federation = outputs["federation_entrypoints.min.json"]
    return_navigation = outputs["return_navigation_hints.min.json"]
    recommended = outputs["recommended_paths.min.json"]
    relation_hints = outputs["kag_source_lift_relation_hints.min.json"]
    composite = outputs["composite_stress_route_hints.min.json"]
    shortlist = outputs["owner_layer_shortlist.min.json"]
    pairing = outputs["pairing_hints.min.json"]
    quest_dispatch_hints = outputs["quest_dispatch_hints.min.json"]
    tiny_model = outputs["tiny_model_entrypoints.json"]

    assert [entry["kind"] for entry in registry["entries"]] == [
        "technique",
        "technique",
        "skill",
        "skill",
        "eval",
        "eval",
        "memo",
        "memo",
    ]
    assert [entry["kind"] for entry in router["entries"]] == [
        "technique",
        "technique",
        "skill",
        "skill",
        "eval",
        "eval",
        "memo",
        "memo",
    ]
    assert {entry["source_type"] for entry in registry["entries"]} == {"generated-catalog"}
    assert relation_hints == {
        "version": 1,
        "scope": "kag_source_lift_family",
        "source_repo": "aoa-techniques",
        "source_catalog": "generated/technique_catalog.min.json",
        "family_ids": KAG_SOURCE_LIFT_TECHNIQUE_IDS,
        "entries": [],
    }
    assert composite["schema_version"] == "aoa_routing_composite_stress_route_hints_v1"
    assert [item["repo"] for item in composite["source_inputs"]] == [
        "aoa-stats",
        "aoa-playbooks",
        "aoa-playbooks",
        "aoa-kag",
        "aoa-kag",
        "aoa-memo",
    ]
    assert composite["hints"][0]["preferred_posture"] == "source_first_until_pass"
    assert composite["hints"][0]["memo_context"] == []
    assert [step["kind"] for step in composite["hints"][0]["next_hops"]] == [
        "source_receipt",
        "playbook_lane",
        "reentry_gate",
        "projection_health",
        "regrounding_ticket",
    ]
    assert quest_dispatch_hints["version"] == 1
    assert quest_dispatch_hints["wave_scope"] == "source-only"
    assert quest_dispatch_hints["actions_enabled"] == ["inspect", "expand", "handoff"]
    assert shortlist["schema_version"] == 1
    assert {
        (entry["signal"], entry["owner_repo"], entry["ambiguity"])
        for entry in shortlist["hints"]
        if entry["signal"] in {"proof-need", "scenario-recurring", "repeated-pattern"}
    } >= {
        ("proof-need", "aoa-evals", "clear"),
        ("scenario-recurring", "aoa-playbooks", "clear"),
        ("scenario-recurring", "aoa-techniques", "ambiguous"),
        ("repeated-pattern", "aoa-techniques", "clear"),
    }
    assert quest_dispatch_hints["source_inputs"] == [
        {"repo": "aoa-techniques", "surface_kind": "quest_catalog", "ref": "generated/quest_catalog.min.json"},
        {"repo": "aoa-techniques", "surface_kind": "quest_dispatch", "ref": "generated/quest_dispatch.min.json"},
        {"repo": "aoa-skills", "surface_kind": "quest_catalog", "ref": "generated/quest_catalog.min.json"},
        {"repo": "aoa-skills", "surface_kind": "quest_dispatch", "ref": "generated/quest_dispatch.min.json"},
        {"repo": "aoa-evals", "surface_kind": "quest_catalog", "ref": "generated/quest_catalog.min.json"},
        {"repo": "aoa-evals", "surface_kind": "quest_dispatch", "ref": "generated/quest_dispatch.min.json"},
    ]
    assert [(hint["repo"], hint["id"]) for hint in quest_dispatch_hints["hints"]] == [
        ("aoa-techniques", "AOA-TECH-Q-0003"),
        ("aoa-techniques", "AOA-TECH-Q-0004"),
        ("aoa-skills", "AOA-SK-Q-0003"),
        ("aoa-skills", "AOA-SK-Q-0004"),
        ("aoa-evals", "AOA-EV-Q-0003"),
        ("aoa-evals", "AOA-EV-Q-0004"),
    ]
    assert quest_dispatch_hints["hints"][0] == {
        "schema_version": "quest_dispatch_hint_v2",
        "id": "AOA-TECH-Q-0003",
        "repo": "aoa-techniques",
        "state": "captured",
        "band": "near",
        "difficulty": "d3_seam",
        "risk": "r2_contract",
        "delegate_tier": "planner",
        "source_path": "quests/AOA-TECH-Q-0003.yaml",
        "public_safe": True,
        "next_actions": [
            {
                "verb": "inspect",
                "target_repo": "aoa-techniques",
                "target_surface": "generated/quest_dispatch.min.json",
                "match_key": "id",
                "target_value": "AOA-TECH-Q-0003",
            },
            {
                "verb": "expand",
                "target_repo": "aoa-techniques",
                "target_surface": "docs/QUESTBOOK_TECHNIQUE_INTEGRATION.md",
                "match_key": "path",
                "target_value": "docs/QUESTBOOK_TECHNIQUE_INTEGRATION.md",
            },
            {
                "verb": "handoff",
                "target_repo": "aoa-routing",
                "target_surface": "generated/federation_entrypoints.min.json",
                "match_key": "id",
                "target_value": "planner",
            },
        ],
        "fallback": {
            "verb": "inspect",
            "target_repo": "aoa-techniques",
            "target_surface": "generated/quest_catalog.min.json",
            "match_key": "id",
            "target_value": "AOA-TECH-Q-0003",
        },
    }

    technique_hint = next(hint for hint in hints["hints"] if hint["kind"] == "technique")
    assert technique_hint["actions"]["inspect"] == {
        "enabled": True,
        "surface_file": "generated/technique_capsules.json",
        "match_field": "id",
    }
    assert technique_hint["actions"]["expand"] == {
        "enabled": True,
        "surface_file": "generated/technique_sections.full.json",
        "match_field": "id",
        "section_key_field": "key",
        "default_sections": [
            "intent",
            "when_to_use",
            "inputs",
            "outputs",
            "core_procedure",
            "contracts",
            "risks",
            "validation",
        ],
        "supported_sections": [
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
    }
    assert technique_hint["actions"]["pair"] == {
        "enabled": True,
        "surface_repo": "aoa-routing",
        "surface_file": "generated/pairing_hints.min.json",
        "match_field": "id",
    }
    assert technique_hint["actions"]["second_cut"] == {
        "enabled": True,
        "surface_repo": "aoa-techniques",
        "surface_file": "generated/technique_kind_manifest.min.json",
        "collection_key": "kinds",
        "match_field": "kind",
        "selection_axis": "kind",
        "prerequisite_axes": ["domain"],
    }
    memo_hint = next(hint for hint in hints["hints"] if hint["kind"] == "memo")
    assert memo_hint == {
        "kind": "memo",
        "enabled": True,
        "source_repo": "aoa-memo",
        "use_when": "need bounded recall or memory-layer doctrine surfaces without copying memo truth into routing",
        "actions": {
            "pick": {"enabled": True},
            "inspect": {
                "enabled": True,
                "surface_file": "generated/memory_catalog.min.json",
                "match_field": "id",
            },
            "expand": {
                "enabled": True,
                "surface_file": "generated/memory_sections.full.json",
                "match_field": "id",
                "section_key_field": "section_id",
                "default_sections": [],
                "supported_sections": [],
            },
            "pair": {"enabled": False},
            "recall": {
                "enabled": True,
                "contract_file": "examples/recall_contract.router.semantic.json",
                "default_mode": "semantic",
                "supported_modes": ["semantic", "source_route", "lineage"],
                "contracts_by_mode": {
                    "semantic": "examples/recall_contract.router.semantic.json",
                    "source_route": "examples/recall_contract.router.source_route.json",
                    "lineage": "examples/recall_contract.router.lineage.json",
                },
                "capsule_surfaces_by_mode": {
                    "semantic": "generated/memory_capsules.json",
                    "lineage": "generated/memory_capsules.json",
                },
                "parallel_families": {
                    "memory_objects": {
                        "inspect_surface": "generated/memory_object_catalog.min.json",
                        "expand_surface": "generated/memory_object_sections.full.json",
                        "default_mode": "working",
                        "supported_modes": ["working", "semantic", "lineage"],
                        "contracts_by_mode": {
                            "working": "examples/recall_contract.object.working.json",
                            "semantic": "examples/recall_contract.object.semantic.json",
                            "lineage": "examples/recall_contract.object.lineage.json",
                        },
                        "capsule_surfaces_by_mode": {
                            "semantic": "generated/memory_object_capsules.json",
                            "lineage": "generated/memory_object_capsules.json",
                        },
                    }
                },
            },
        },
    }
    assert tier_hints["source_of_truth"] == {
        "tier_registry_repo": "aoa-agents",
        "tier_registry_path": "generated/model_tier_registry.json",
    }
    assert tier_hints["hints"][0] == {
        "task_family": "task-triage",
        "preferred_tier": "router",
        "fallback_tier": "planner",
        "use_when": "need the fastest classification of task shape, risk, and smallest next step",
        "output_artifact": "route_decision",
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
    assert by_key[("memo", "AOA-M-0001")] == {
        "kind": "memo",
        "id": "AOA-M-0001",
        "upstream": [],
        "downstream": [],
    }

    pairing_by_key = {(entry["kind"], entry["id"]): entry for entry in pairing["entries"]}
    assert pairing_by_key[("technique", "AOA-T-0001")] == {
        "kind": "technique",
        "id": "AOA-T-0001",
        "pairs": [
            {"kind": "skill", "id": "aoa-change-protocol", "relation": "required_by"},
            {"kind": "eval", "id": "aoa-bounded-change-quality", "relation": "required_by"},
        ],
    }
    assert pairing_by_key[("skill", "aoa-context-scan")] == {
        "kind": "skill",
        "id": "aoa-context-scan",
        "pairs": [
            {"kind": "technique", "id": "AOA-T-0002", "relation": "requires"},
            {"kind": "eval", "id": "aoa-context-scan-quality", "relation": "required_by"},
        ],
    }
    assert federation["version"] == 1
    assert federation["active_entry_kinds"] == [
        "agent",
        "tier",
        "playbook",
        "kag_view",
        "seed",
        "runtime_surface",
        "orientation_surface",
    ]
    assert federation["declared_entry_kinds"] == ["tos_node"]
    assert return_navigation["version"] == 1
    memo_return = next(
        record for record in return_navigation["thin_router_returns"] if record["context_kind"] == "memo"
    )
    assert memo_return == {
        "context_kind": "memo",
        "source_repo": "aoa-memo",
        "supported_return_reasons": [
            "checkpoint_continuity_needed",
            "artifact_contract_lost",
            "source_boundary_lost",
        ],
        "primary_action": {
            "verb": "recall",
            "target_repo": "aoa-memo",
            "target_surface": "examples/recall_contract.object.working.return.json",
        },
        "secondary_action": {
            "verb": "inspect",
            "target_repo": "aoa-memo",
            "target_surface": "generated/memory_object_catalog.min.json",
            "match_field": "id",
        },
        "ownership_note": "Checkpoint continuity and recall meaning stay in aoa-memo; routing only points back to the public return-ready contract and object surface.",
    }
    aoa_root_return = next(
        record for record in return_navigation["federation_root_returns"] if record["root_id"] == "aoa-root"
    )
    assert aoa_root_return["primary_action"] == {
        "verb": "inspect",
        "target_repo": "Agents-of-Abyss",
        "target_surface": "CHARTER.md",
    }
    tos_root_return = next(
        record for record in return_navigation["federation_root_returns"] if record["root_id"] == "tos-root"
    )
    assert tos_root_return["secondary_action"] == {
        "verb": "inspect",
        "target_repo": "Tree-of-Sophia",
        "target_surface": "examples/tos_tiny_entry_route.example.json",
        "match_field": "route_id",
        "target_value": "tos-tiny-entry.zarathustra-prologue",
    }
    playbook_return = next(
        record
        for record in return_navigation["federation_kind_returns"]
        if record["entry_kind"] == "playbook"
    )
    assert playbook_return["primary_action"] == {
        "verb": "inspect",
        "target_repo": "aoa-playbooks",
        "target_surface": "generated/playbook_registry.min.json",
    }
    assert playbook_return["fallback_action"] == {
        "verb": "inspect",
        "target_repo": "aoa-routing",
        "target_surface": "generated/federation_entrypoints.min.json",
        "match_field": "kind",
        "target_value": "playbook",
    }
    seed_return = next(
        record
        for record in return_navigation["federation_kind_returns"]
        if record["entry_kind"] == "seed"
    )
    assert seed_return["primary_action"] == {
        "verb": "inspect",
        "target_repo": "Dionysus",
        "target_surface": "generated/seed_route_map.min.json",
    }
    runtime_return = next(
        record
        for record in return_navigation["federation_kind_returns"]
        if record["entry_kind"] == "runtime_surface"
    )
    assert runtime_return["primary_action"] == {
        "verb": "inspect",
        "target_repo": "aoa-sdk",
        "target_surface": "generated/workspace_control_plane.min.json",
    }
    orientation_return = next(
        record
        for record in return_navigation["federation_kind_returns"]
        if record["entry_kind"] == "orientation_surface"
    )
    assert orientation_return["primary_action"] == {
        "verb": "inspect",
        "target_repo": "8Dionysus",
        "target_surface": "generated/public_route_map.min.json",
    }
    entry_returns = return_navigation["federation_entry_returns"]
    assert entry_returns["aoa-sdk-control-plane"]["primary_action"] == {
        "verb": "inspect",
        "target_repo": "aoa-sdk",
        "target_surface": "generated/workspace_control_plane.min.json",
    }
    assert entry_returns["aoa-sdk-control-plane"]["fallback_action"] == {
        "verb": "inspect",
        "target_repo": "aoa-routing",
        "target_surface": "generated/federation_entrypoints.min.json",
        "match_field": "id",
        "target_value": "aoa-sdk-control-plane",
    }
    assert entry_returns["aoa-stats-summary-catalog"]["primary_action"] == {
        "verb": "inspect",
        "target_repo": "aoa-stats",
        "target_surface": "generated/summary_surface_catalog.min.json",
    }
    assert entry_returns["abyss-stack-diagnostic-spine"]["primary_action"] == {
        "verb": "inspect",
        "target_repo": "abyss-stack",
        "target_surface": "generated/diagnostic_surface_catalog.min.json",
    }
    assert entry_returns["dionysus-seed-garden"]["primary_action"] == {
        "verb": "inspect",
        "target_repo": "Dionysus",
        "target_surface": "generated/seed_route_map.min.json",
    }
    assert entry_returns["8dionysus-public-route-map"]["primary_action"] == {
        "verb": "inspect",
        "target_repo": "8Dionysus",
        "target_surface": "generated/public_route_map.min.json",
    }
    assert federation["source_inputs"][1:3] == [
        {
            "name": "tos_root_readme",
            "repo": "Tree-of-Sophia",
            "role": "root_entry",
            "ref": "README.md",
        },
        {
            "name": "tos_tiny_entry_route",
            "repo": "Tree-of-Sophia",
            "role": "tiny_entry_handoff",
            "ref": "examples/tos_tiny_entry_route.example.json",
        },
    ]
    assert {
        (entry["name"], entry["ref"])
        for entry in federation["source_inputs"]
        if entry["repo"] in {"aoa-sdk", "Dionysus", "abyss-stack"}
    } >= {
        ("aoa_sdk_workspace_control_plane", "generated/workspace_control_plane.min.json"),
        ("dionysus_seed_route_map", "generated/seed_route_map.min.json"),
        ("abyss_stack_diagnostic_surface_catalog", "generated/diagnostic_surface_catalog.min.json"),
    }
    assert tiny_model["queries"][0] == {
        "verb": "pick",
        "source_repo": "aoa-routing",
        "target_surface": "generated/aoa_router.min.json",
        "match_key": "kind",
        "allowed_kinds": ["technique", "skill", "eval", "memo"],
    }
    assert tiny_model["version"] == 2
    assert tiny_model["queries"][-2:] == [
        {
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
        },
        {
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "recall_family": "memory_objects",
        },
    ]

    assert tiny_model["starters"] == [
        {
            "name": "router-root",
            "verb": "pick",
            "source_repo": "aoa-routing",
            "target_surface": "generated/aoa_router.min.json",
            "match_key": "kind",
            "allowed_kinds": ["technique", "skill", "eval", "memo"],
        },
        {
            "name": "technique-root",
            "verb": "pick",
            "source_repo": "aoa-routing",
            "target_surface": "generated/aoa_router.min.json",
            "match_key": "kind",
            "allowed_kinds": ["technique"],
            "target_kind": "technique",
            "target_value": "technique",
        },
        {
            "name": "skill-root",
            "verb": "pick",
            "source_repo": "aoa-routing",
            "target_surface": "generated/aoa_router.min.json",
            "match_key": "kind",
            "allowed_kinds": ["skill"],
            "target_kind": "skill",
            "target_value": "skill",
        },
        {
            "name": "eval-root",
            "verb": "pick",
            "source_repo": "aoa-routing",
            "target_surface": "generated/aoa_router.min.json",
            "match_key": "kind",
            "allowed_kinds": ["eval"],
            "target_kind": "eval",
            "target_value": "eval",
        },
        {
            "name": "memo-root",
            "verb": "pick",
            "source_repo": "aoa-routing",
            "target_surface": "generated/aoa_router.min.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
        },
        {
            "name": "memo-recall-semantic",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_mode": "semantic",
        },
        {
            "name": "memo-recall-source-route",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_mode": "source_route",
        },
        {
            "name": "memo-recall-lineage",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_mode": "lineage",
        },
        {
            "name": "memo-object-recall-working",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_family": "memory_objects",
            "recall_mode": "working",
        },
        {
            "name": "memo-object-recall-semantic",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_family": "memory_objects",
            "recall_mode": "semantic",
        },
        {
            "name": "memo-object-recall-lineage",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_family": "memory_objects",
            "recall_mode": "lineage",
        },
    ]
    assert tiny_model["federation_queries"] == [
        {
            "name": "federation-kind-pick",
            "verb": "pick",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "kind",
            "allowed_entry_kinds": [
                "agent",
                "tier",
                "playbook",
                "kag_view",
                "seed",
                "runtime_surface",
                "orientation_surface",
            ],
        },
        {
            "name": "federation-entry-inspect",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "allowed_entry_kinds": [
                "agent",
                "tier",
                "playbook",
                "kag_view",
                "seed",
                "runtime_surface",
                "orientation_surface",
            ],
        },
        {
            "name": "federation-root-inspect",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "allowed_root_ids": ["aoa-root", "tos-root"],
        },
    ]
    assert tiny_model["federation_starters"] == [
        {
            "name": "federation-root",
            "verb": "pick",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
        },
        {
            "name": "aoa-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "aoa-root",
        },
        {
            "name": "tos-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "tos-root",
        },
        {
            "name": "agent-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "AOA-A-0001",
            "entry_kind": "agent",
        },
        {
            "name": "tier-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "router",
            "entry_kind": "tier",
        },
        {
            "name": "playbook-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "AOA-P-0008",
            "entry_kind": "playbook",
        },
        {
            "name": "kag-view-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "aoa-techniques",
            "entry_kind": "kag_view",
        },
        {
            "name": "seed-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "dionysus-seed-garden",
            "entry_kind": "seed",
        },
        {
            "name": "runtime-surface-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "aoa-sdk-control-plane",
            "entry_kind": "runtime_surface",
        },
        {
            "name": "orientation-surface-root",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "8dionysus-public-route-map",
            "entry_kind": "orientation_surface",
        },
    ]


def test_validate_generated_dir_matches_outputs_accepts_fixture_build(tmp_path: Path) -> None:
    outputs = build_fixture_outputs()
    generated_dir = tmp_path / "generated"
    for filename, payload in outputs.items():
        write_output(generated_dir / filename, payload)

    mismatches = build_router.validate_generated_dir_matches_outputs(outputs, generated_dir=generated_dir)
    assert mismatches == []


def test_validate_generated_dir_matches_outputs_rejects_stale_output(tmp_path: Path) -> None:
    outputs = build_fixture_outputs()
    generated_dir = tmp_path / "generated"
    for filename, payload in outputs.items():
        write_output(generated_dir / filename, payload)

    stale_path = generated_dir / "aoa_router.min.json"
    stale_payload = json.loads(stale_path.read_text(encoding="utf-8"))
    stale_payload["entries"][0]["summary"] = "stale router output"
    write_output(stale_path, stale_payload)

    mismatches = build_router.validate_generated_dir_matches_outputs(outputs, generated_dir=generated_dir)
    assert mismatches == [f"stale generated output: {stale_path.as_posix()}"]


def test_build_outputs_publish_federation_entry_abi_from_fixtures() -> None:
    outputs = build_fixture_outputs()
    federation = outputs["federation_entrypoints.min.json"]

    root_by_id = {entry["id"]: entry for entry in federation["root_entries"]}
    entry_by_key = {
        (entry["kind"], entry["id"]): entry for entry in federation["entrypoints"]
    }

    aoa_root = root_by_id["aoa-root"]
    assert aoa_root["capsule_surface"] == "Agents-of-Abyss:README.md"
    assert aoa_root["authority_surface"] == "Agents-of-Abyss:CHARTER.md"
    assert aoa_root["fallback"] == {
        "verb": "pick",
        "target_repo": "aoa-routing",
        "target_surface": "generated/aoa_router.min.json",
        "match_key": "kind",
        "target_value": "technique",
    }
    assert aoa_root["next_hops"] == [
        {"kind": "tier", "id": "router"},
        {"kind": "playbook", "id": "AOA-P-0008"},
        {"kind": "kag_view", "id": "aoa-techniques"},
    ]

    tos_root = root_by_id["tos-root"]
    assert tos_root["capsule_surface"] == "Tree-of-Sophia:README.md"
    assert tos_root["authority_surface"] == "Tree-of-Sophia:CHARTER.md"
    assert tos_root["next_actions"] == [
        {
            "verb": "inspect",
            "target_repo": "Tree-of-Sophia",
            "target_surface": "examples/tos_tiny_entry_route.example.json",
            "match_key": "route_id",
            "target_value": "tos-tiny-entry.zarathustra-prologue",
        },
        {
            "verb": "inspect",
            "target_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "Tree-of-Sophia",
        },
        {
            "verb": "inspect",
            "target_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "AOA-P-0009",
        },
    ]
    assert tos_root["fallback"] == {
        "verb": "inspect",
        "target_repo": "aoa-routing",
        "target_surface": "generated/federation_entrypoints.min.json",
        "match_key": "id",
        "target_value": "aoa-root",
    }
    assert tos_root["next_hops"] == [
        {"kind": "kag_view", "id": "Tree-of-Sophia"},
        {"kind": "playbook", "id": "AOA-P-0009"},
    ]
    assert "source-owned tiny-entry route" in tos_root["risk"]

    router_tier = entry_by_key[("tier", "router")]
    assert router_tier["capsule_surface"] == "aoa-agents:generated/model_tier_registry.json"
    assert router_tier["authority_surface"] == "aoa-agents:model_tiers/router.tier.json"
    assert router_tier["fallback"] == {
        "verb": "inspect",
        "target_repo": "aoa-routing",
        "target_surface": "generated/federation_entrypoints.min.json",
        "match_key": "id",
        "target_value": "AOA-A-0001",
    }
    assert router_tier["next_hops"] == [{"kind": "agent", "id": "AOA-A-0001"}]

    kag_view = entry_by_key[("kag_view", "aoa-techniques")]
    assert kag_view["capsule_surface"] == "aoa-kag:generated/federation_spine.min.json"
    assert kag_view["authority_surface"] == "aoa-kag:docs/FEDERATION_SPINE.md"
    assert kag_view["next_actions"] == [
        {
            "verb": "inspect",
            "target_repo": "aoa-techniques",
            "target_surface": "generated/repo_doc_surface_manifest.min.json",
            "match_key": "doc_id",
            "target_value": "readme",
        },
        {
            "verb": "inspect",
            "target_repo": "aoa-techniques",
            "target_surface": "generated/technique_catalog.min.json",
            "match_key": "id",
            "target_value": "AOA-T-0001",
        },
    ]
    assert kag_view["next_hops"] == [
        {"kind": "tier", "id": "router"},
        {"kind": "playbook", "id": "AOA-P-0008"},
    ]

    tos_kag_view = entry_by_key[("kag_view", "Tree-of-Sophia")]
    assert tos_kag_view["capsule_surface"] == "aoa-kag:generated/federation_spine.min.json"
    assert tos_kag_view["authority_surface"] == "aoa-kag:docs/FEDERATION_SPINE.md"
    assert tos_kag_view["next_actions"] == [
        {
            "verb": "inspect",
            "target_repo": "Tree-of-Sophia",
            "target_surface": "docs/TINY_ENTRY_ROUTE.md",
            "match_key": "path",
            "target_value": "docs/TINY_ENTRY_ROUTE.md",
        },
        {
            "verb": "inspect",
            "target_repo": "Tree-of-Sophia",
            "target_surface": "examples/tos_tiny_entry_route.example.json",
            "match_key": "route_id",
            "target_value": "tos-tiny-entry.zarathustra-prologue",
        },
        {
            "verb": "inspect",
            "target_repo": "aoa-kag",
            "target_surface": "generated/tos_zarathustra_route_retrieval_pack.min.json",
            "match_key": "retrieval_id",
            "target_value": "AOA-K-0011::thus-spoke-zarathustra/prologue-1",
        },
    ]
    assert tos_kag_view["next_hops"] == [
        {"kind": "tier", "id": "router"},
        {"kind": "playbook", "id": "AOA-P-0009"},
    ]
    assert "Tree-of-Sophia remains authoritative" in tos_kag_view["risk"]

    seed_entry = entry_by_key[("seed", "dionysus-seed-garden")]
    assert seed_entry["capsule_surface"] == "Dionysus:generated/seed_route_map.min.json"
    assert seed_entry["authority_surface"] == "Dionysus:docs/codex/planting-protocol.md"
    assert seed_entry["next_hops"] == [
        {"kind": "orientation_surface", "id": "8dionysus-public-route-map"},
        {"kind": "runtime_surface", "id": "aoa-sdk-control-plane"},
    ]

    sdk_runtime_entry = entry_by_key[("runtime_surface", "aoa-sdk-control-plane")]
    assert (
        sdk_runtime_entry["capsule_surface"]
        == "aoa-sdk:generated/workspace_control_plane.min.json"
    )
    assert sdk_runtime_entry["authority_surface"] == "aoa-sdk:docs/boundaries.md"

    stats_runtime_entry = entry_by_key[("runtime_surface", "aoa-stats-summary-catalog")]
    assert (
        stats_runtime_entry["capsule_surface"]
        == "aoa-stats:generated/summary_surface_catalog.min.json"
    )

    abyss_runtime_entry = entry_by_key[("runtime_surface", "abyss-stack-diagnostic-spine")]
    assert (
        abyss_runtime_entry["capsule_surface"]
        == "abyss-stack:generated/diagnostic_surface_catalog.min.json"
    )

    profile_entry = entry_by_key[("orientation_surface", "8dionysus-public-route-map")]
    assert profile_entry["capsule_surface"] == "8Dionysus:generated/public_route_map.min.json"


def test_build_outputs_reject_tos_kag_view_spine_drift(tmp_path: Path) -> None:
    kag_root = tmp_path / "aoa-kag"
    shutil.copytree(FIXTURES_ROOT / "aoa-kag", kag_root)
    spine_path = kag_root / "generated" / "federation_spine.min.json"
    payload = json.loads(spine_path.read_text(encoding="utf-8"))
    payload["repos"][1]["current_entry_surface_refs"] = ["Tree-of-Sophia/README.md"]
    write_json(spine_path, payload)

    with pytest.raises(build_router.RouterError, match="current_entry_surface_refs must stay"):
        build_fixture_outputs(kag_root=kag_root)


def test_build_outputs_accept_compact_kag_spine_entries(tmp_path: Path) -> None:
    kag_root = tmp_path / "aoa-kag"
    shutil.copytree(FIXTURES_ROOT / "aoa-kag", kag_root)
    spine_path = kag_root / "generated" / "federation_spine.min.json"
    payload = json.loads(spine_path.read_text(encoding="utf-8"))
    payload["repos"] = [
        {
            "repo": "aoa-techniques",
            "pilot_posture": "source_owned_export_tiny",
            "export_ref": "aoa-techniques/generated/kag_export.min.json",
            "kind": "technique",
            "object_id": "AOA-T-0043",
            "entry_surface_ref": "aoa-techniques/generated/technique_capsules.json",
            "adjunct_surfaces": [],
            "summary_50": payload["repos"][0]["provenance_note"],
            "provenance_note": payload["repos"][0]["provenance_note"],
            "non_identity_boundary": payload["repos"][0]["non_identity_boundary"],
        },
        {
            "repo": "Tree-of-Sophia",
            "pilot_posture": "source_owned_export_tiny",
            "export_ref": "Tree-of-Sophia/generated/kag_export.min.json",
            "kind": "source_node",
            "object_id": "tos.source.thus-spoke-zarathustra.prologue",
            "entry_surface_ref": "Tree-of-Sophia/examples/source_node.example.json",
            "adjunct_surfaces": [
                {
                    "surface_id": "AOA-K-0011",
                    "surface_name": "tos-zarathustra-route-retrieval-surface",
                    "surface_ref": "generated/tos_zarathustra_route_retrieval_pack.min.json",
                    "match_key": "retrieval_id",
                    "target_value": "AOA-K-0011::thus-spoke-zarathustra/prologue-1",
                    "route_id": "thus-spoke-zarathustra/prologue-1",
                }
            ],
            "summary_50": payload["repos"][1]["provenance_note"],
            "provenance_note": payload["repos"][1]["provenance_note"],
            "non_identity_boundary": payload["repos"][1]["non_identity_boundary"],
        },
    ]
    write_json(spine_path, payload)

    outputs = build_fixture_outputs(kag_root=kag_root)

    entry_by_key = {
        (entry["kind"], entry["id"]): entry
        for entry in outputs["federation_entrypoints.min.json"]["entrypoints"]
    }
    assert entry_by_key[("kag_view", "aoa-techniques")]["next_actions"] == [
        {
            "verb": "inspect",
            "target_repo": "aoa-techniques",
            "target_surface": "generated/repo_doc_surface_manifest.min.json",
            "match_key": "doc_id",
            "target_value": "readme",
        },
        {
            "verb": "inspect",
            "target_repo": "aoa-techniques",
            "target_surface": "generated/technique_catalog.min.json",
            "match_key": "id",
            "target_value": "AOA-T-0001",
        },
    ]
    assert entry_by_key[("kag_view", "Tree-of-Sophia")]["next_actions"] == [
        {
            "verb": "inspect",
            "target_repo": "Tree-of-Sophia",
            "target_surface": "docs/TINY_ENTRY_ROUTE.md",
            "match_key": "path",
            "target_value": "docs/TINY_ENTRY_ROUTE.md",
        },
        {
            "verb": "inspect",
            "target_repo": "Tree-of-Sophia",
            "target_surface": "examples/tos_tiny_entry_route.example.json",
            "match_key": "route_id",
            "target_value": "tos-tiny-entry.zarathustra-prologue",
        },
        {
            "verb": "inspect",
            "target_repo": "aoa-kag",
            "target_surface": "generated/tos_zarathustra_route_retrieval_pack.min.json",
            "match_key": "retrieval_id",
            "target_value": "AOA-K-0011::thus-spoke-zarathustra/prologue-1",
        },
    ]


def test_build_outputs_lifts_kag_source_family_relations(tmp_path: Path) -> None:
    techniques_root = tmp_path / "aoa-techniques"
    shutil.copytree(FIXTURES_ROOT / "aoa-techniques", techniques_root)
    catalog_path = techniques_root / "generated" / "technique_catalog.min.json"
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    payload["techniques"].extend(build_kag_source_lift_technique_entries())
    write_json(catalog_path, payload)

    outputs = build_fixture_outputs(techniques_root=techniques_root)

    relation_hints = outputs["kag_source_lift_relation_hints.min.json"]
    pairing = outputs["pairing_hints.min.json"]
    tiny_model = outputs["tiny_model_entrypoints.json"]
    assert relation_hints["family_ids"] == KAG_SOURCE_LIFT_TECHNIQUE_IDS
    by_id = {entry["id"]: entry for entry in relation_hints["entries"]}
    assert by_id["AOA-T-0018"]["relations"] == [
        {"type": "complements", "target": "AOA-T-0019"}
    ]
    assert by_id["AOA-T-0019"]["relations"] == [
        {"type": "complements", "target": "AOA-T-0018"},
        {"type": "used_together_for", "target": "AOA-T-0020"},
        {"type": "used_together_for", "target": "AOA-T-0021"},
    ]
    assert by_id["AOA-T-0021"]["relations"] == [
        {"type": "requires", "target": "AOA-T-0019"}
    ]
    pairing_by_id = {entry["id"]: entry for entry in pairing["entries"] if entry["kind"] == "technique"}
    assert pairing_by_id["AOA-T-0019"]["pairs"] == [
        {"kind": "technique", "id": "AOA-T-0018", "relation": "complements"},
        {"kind": "technique", "id": "AOA-T-0020", "relation": "used_together_for"},
        {"kind": "technique", "id": "AOA-T-0021", "relation": "used_together_for"},
    ]
    assert tiny_model["starters"][-2:] == [
        {
            "name": "kag-source-lift-default",
            "verb": "inspect",
            "source_repo": "aoa-techniques",
            "target_surface": "generated/technique_capsules.json",
            "match_key": "id",
            "allowed_kinds": ["technique"],
            "target_kind": "technique",
            "target_value": "AOA-T-0019",
        },
        {
            "name": "kag-source-lift-companions",
            "verb": "pair",
            "source_repo": "aoa-routing",
            "target_surface": "generated/pairing_hints.min.json",
            "match_key": "id",
            "allowed_kinds": ["technique"],
            "target_kind": "technique",
            "target_value": "AOA-T-0019",
        },
    ]


def test_build_outputs_limits_tiny_model_recall_modes_to_router_ready_contracts(tmp_path: Path) -> None:
    memo_root = tmp_path / "aoa-memo"
    shutil.copytree(FIXTURES_ROOT / "aoa-memo", memo_root)
    (memo_root / "examples" / "recall_contract.router.source_route.json").unlink()
    (memo_root / "examples" / "recall_contract.router.lineage.json").unlink()

    outputs = build_fixture_outputs(memo_root=memo_root)

    memo_hint = next(
        hint for hint in outputs["task_to_surface_hints.json"]["hints"] if hint["kind"] == "memo"
    )
    assert memo_hint["actions"]["recall"] == {
        "enabled": True,
        "contract_file": "examples/recall_contract.router.semantic.json",
        "default_mode": "semantic",
        "supported_modes": ["semantic"],
        "contracts_by_mode": {
            "semantic": "examples/recall_contract.router.semantic.json",
        },
        "capsule_surfaces_by_mode": {
            "semantic": "generated/memory_capsules.json",
        },
        "parallel_families": {
            "memory_objects": {
                "inspect_surface": "generated/memory_object_catalog.min.json",
                "expand_surface": "generated/memory_object_sections.full.json",
                "default_mode": "working",
                "supported_modes": ["working", "semantic", "lineage"],
                "contracts_by_mode": {
                    "working": "examples/recall_contract.object.working.json",
                    "semantic": "examples/recall_contract.object.semantic.json",
                    "lineage": "examples/recall_contract.object.lineage.json",
                },
                "capsule_surfaces_by_mode": {
                    "semantic": "generated/memory_object_capsules.json",
                    "lineage": "generated/memory_object_capsules.json",
                },
            }
        },
    }
    recall_starters = [
        starter
        for starter in outputs["tiny_model_entrypoints.json"]["starters"]
        if starter["verb"] == "recall"
    ]
    assert recall_starters == [
        {
            "name": "memo-recall-semantic",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_mode": "semantic",
        },
        {
            "name": "memo-object-recall-working",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_family": "memory_objects",
            "recall_mode": "working",
        },
        {
            "name": "memo-object-recall-semantic",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_family": "memory_objects",
            "recall_mode": "semantic",
        },
        {
            "name": "memo-object-recall-lineage",
            "verb": "recall",
            "source_repo": "aoa-routing",
            "target_surface": "generated/task_to_surface_hints.json",
            "match_key": "kind",
            "allowed_kinds": ["memo"],
            "target_kind": "memo",
            "target_value": "memo",
            "recall_family": "memory_objects",
            "recall_mode": "lineage",
        },
    ]


def test_build_outputs_omits_parallel_object_family_when_object_contract_is_missing(tmp_path: Path) -> None:
    memo_root = tmp_path / "aoa-memo"
    shutil.copytree(FIXTURES_ROOT / "aoa-memo", memo_root)
    (memo_root / "examples" / "recall_contract.object.lineage.json").unlink()

    outputs = build_fixture_outputs(memo_root=memo_root)

    memo_hint = next(
        hint for hint in outputs["task_to_surface_hints.json"]["hints"] if hint["kind"] == "memo"
    )
    assert "parallel_families" not in memo_hint["actions"]["recall"]
    assert all(
        starter.get("recall_family") != "memory_objects"
        for starter in outputs["tiny_model_entrypoints.json"]["starters"]
        if starter["verb"] == "recall"
    )
    assert all(
        query.get("recall_family") != "memory_objects"
        for query in outputs["tiny_model_entrypoints.json"]["queries"]
        if query["verb"] == "recall"
    )


def test_build_outputs_omits_parallel_object_family_when_object_surface_is_missing(tmp_path: Path) -> None:
    memo_root = tmp_path / "aoa-memo"
    shutil.copytree(FIXTURES_ROOT / "aoa-memo", memo_root)
    (memo_root / "generated" / "memory_object_sections.full.json").unlink()

    outputs = build_fixture_outputs(memo_root=memo_root)

    memo_hint = next(
        hint for hint in outputs["task_to_surface_hints.json"]["hints"] if hint["kind"] == "memo"
    )
    assert "parallel_families" not in memo_hint["actions"]["recall"]
    assert all(
        starter.get("recall_family") != "memory_objects"
        for starter in outputs["tiny_model_entrypoints.json"]["starters"]
        if starter["verb"] == "recall"
    )
    assert all(
        query.get("recall_family") != "memory_objects"
        for query in outputs["tiny_model_entrypoints.json"]["queries"]
        if query["verb"] == "recall"
    )


def test_build_uses_catalog_only_ingestion_for_skills_and_evals(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    evals_root = tmp_path / "aoa-evals"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    shutil.copytree(FIXTURES_ROOT / "aoa-evals", evals_root)
    shutil.rmtree(skills_root / "skills")
    shutil.rmtree(evals_root / "bundles")

    outputs = build_fixture_outputs(skills_root=skills_root, evals_root=evals_root)

    assert len(outputs["cross_repo_registry.min.json"]["entries"]) == 8


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

    outputs = build_fixture_outputs(skills_root=skills_root)

    registry_entries = outputs["cross_repo_registry.min.json"]["entries"]
    skill_entry = next(entry for entry in registry_entries if entry["id"] == "aoa-context-scan")
    assert skill_entry["attributes"]["technique_dependencies"] == ["AOA-T-PENDING-CONTEXT-SCAN"]

    by_key = {
        (entry["kind"], entry["id"]): entry
        for entry in outputs["recommended_paths.min.json"]["entries"]
    }
    assert by_key[("skill", "aoa-context-scan")]["upstream"] == []


def test_build_outputs_composite_stress_hints_include_memo_recovery_context(
    tmp_path: Path,
) -> None:
    roots = {}
    for repo_name in FIXTURE_REPO_NAMES:
        target = tmp_path / repo_name
        shutil.copytree(FIXTURES_ROOT / repo_name, target)
        roots[repo_name] = target

    catalog_path = roots["aoa-memo"] / "generated" / "memory_object_catalog.min.json"
    catalog_payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog_payload["memory_objects"].append(
        {
            "id": "memo.pattern.2026-04-07.antifragility-stress-recovery-window",
            "kind": "pattern",
            "title": "Stress recovery stays bounded only when replay follows source receipt, gate, and regrounding order",
            "summary": "Reviewed recovery pattern for the fourth-wave stress window.",
            "scope_classes": ["repo", "project"],
            "temperature": "cool",
            "review_state": "confirmed",
            "current_recall_status": "preferred",
            "authority_kind": "human_reviewed",
            "primary_recall_modes": ["procedural", "semantic"],
            "source_path": "examples/pattern.antifragility-stress-recovery-window.example.json",
            "inspect_key": "memo.pattern.2026-04-07.antifragility-stress-recovery-window",
            "expand_key": "memo.pattern.2026-04-07.antifragility-stress-recovery-window",
        }
    )
    write_json(catalog_path, catalog_payload)

    outputs = build_router.build_outputs(
        roots["aoa-techniques"],
        roots["aoa-skills"],
        roots["aoa-evals"],
        roots["aoa-memo"],
        roots["aoa-stats"],
        roots["aoa-agents"],
        roots["Agents-of-Abyss"],
        roots["aoa-playbooks"],
        roots["aoa-kag"],
        roots["Tree-of-Sophia"],
        roots["aoa-sdk"],
        roots["Dionysus"],
        roots["8Dionysus"],
        roots["abyss-stack"],
    )

    hint = outputs["composite_stress_route_hints.min.json"]["hints"][0]
    assert hint["input_refs"]["memo_pattern_refs"] == [
        "aoa-memo:examples/pattern.antifragility-stress-recovery-window.example.json"
    ]
    assert hint["memo_context"] == [
        {
            "memory_id": "memo.pattern.2026-04-07.antifragility-stress-recovery-window",
            "title": "Stress recovery stays bounded only when replay follows source receipt, gate, and regrounding order",
            "source_path": "examples/pattern.antifragility-stress-recovery-window.example.json",
            "review_state": "confirmed",
            "current_recall_status": "preferred",
        }
    ]
    assert hint["next_hops"][-1] == {
        "kind": "memo_pattern",
        "target_repo": "aoa-memo",
        "target_surface": "examples/pattern.antifragility-stress-recovery-window.example.json",
        "reason": "Reviewed recovery-pattern context may be recalled after source receipts and re-entry gates are named.",
        "bounded": True,
    }


def test_build_is_deterministic_on_repeated_runs(tmp_path: Path) -> None:
    generated_dir = tmp_path / "generated"
    outputs_a = build_fixture_outputs()
    for filename, payload in outputs_a.items():
        write_output(generated_dir / filename, payload)
    snapshot_a = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(generated_dir.iterdir())
    }

    outputs_b = build_fixture_outputs()
    for filename, payload in outputs_b.items():
        write_output(generated_dir / filename, payload)
    snapshot_b = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(generated_dir.iterdir())
    }

    assert snapshot_a == snapshot_b


def test_owner_layer_shortlist_includes_explicit_and_ambiguous_family_hints() -> None:
    outputs = build_fixture_outputs()

    shortlist = outputs["owner_layer_shortlist.min.json"]
    explicit_skill = next(
        entry
        for entry in shortlist["hints"]
        if entry["signal"] == "explicit-request" and entry["owner_repo"] == "aoa-skills"
    )
    recurring_entries = [
        entry
        for entry in shortlist["hints"]
        if entry["signal"] == "scenario-recurring"
    ]
    explicit_seed = next(
        entry
        for entry in shortlist["hints"]
        if entry["signal"] == "explicit-request" and entry["owner_repo"] == "Dionysus"
    )
    explicit_runtime = next(
        entry
        for entry in shortlist["hints"]
        if entry["signal"] == "explicit-request" and entry["owner_repo"] == "abyss-stack"
    )

    assert explicit_skill["target_surface"] == "aoa-skills.runtime_discovery_index"
    assert explicit_seed["target_surface"] == "Dionysus.seed_route_map.min"
    assert explicit_runtime["target_surface"] == "abyss-stack.diagnostic_surface_catalog.min"
    assert explicit_skill["confidence"] == "high"
    assert {entry["owner_repo"] for entry in recurring_entries} == {
        "aoa-playbooks",
        "aoa-techniques",
    }
    assert {entry["ambiguity"] for entry in recurring_entries} == {"clear", "ambiguous"}


def test_build_task_to_tier_hints_reads_agents_registry_artifacts(tmp_path: Path) -> None:
    agents_root = tmp_path / "aoa-agents"
    shutil.copytree(FIXTURES_ROOT / "aoa-agents", agents_root)
    registry_path = agents_root / "generated" / "model_tier_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["model_tiers"][0]["artifact_requirement"] = "triage_packet"
    write_json(registry_path, payload)

    outputs = build_fixture_outputs(agents_root=agents_root)

    assert outputs["task_to_tier_hints.json"]["hints"][0]["output_artifact"] == "triage_packet"
