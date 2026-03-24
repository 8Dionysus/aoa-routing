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
    "aoa-agents",
    "Agents-of-Abyss",
    "aoa-playbooks",
    "aoa-kag",
    "Tree-of-Sophia",
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


def build_fixture_outputs(
    *,
    techniques_root: Path = FIXTURES_ROOT / "aoa-techniques",
    skills_root: Path = FIXTURES_ROOT / "aoa-skills",
    evals_root: Path = FIXTURES_ROOT / "aoa-evals",
    memo_root: Path = FIXTURES_ROOT / "aoa-memo",
    agents_root: Path = FIXTURES_ROOT / "aoa-agents",
    aoa_root: Path = FIXTURES_ROOT / "Agents-of-Abyss",
    playbooks_root: Path = FIXTURES_ROOT / "aoa-playbooks",
    kag_root: Path = FIXTURES_ROOT / "aoa-kag",
    tos_root: Path = FIXTURES_ROOT / "Tree-of-Sophia",
) -> dict[str, dict[str, object]]:
    return build_router.build_outputs(
        techniques_root,
        skills_root,
        evals_root,
        memo_root,
        agents_root,
        aoa_root,
        playbooks_root,
        kag_root,
        tos_root,
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
    recommended = outputs["recommended_paths.min.json"]
    relation_hints = outputs["kag_source_lift_relation_hints.min.json"]
    pairing = outputs["pairing_hints.min.json"]
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
    assert federation["active_entry_kinds"] == ["agent", "tier", "playbook", "kag_view"]
    assert federation["declared_entry_kinds"] == ["seed", "tos_node", "runtime_surface"]
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
            "allowed_entry_kinds": ["agent", "tier", "playbook", "kag_view"],
        },
        {
            "name": "federation-entry-inspect",
            "verb": "inspect",
            "source_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "allowed_entry_kinds": ["agent", "tier", "playbook", "kag_view"],
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
    ]


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
    assert tos_root["fallback"] == {
        "verb": "inspect",
        "target_repo": "aoa-routing",
        "target_surface": "generated/federation_entrypoints.min.json",
        "match_key": "id",
        "target_value": "aoa-root",
    }
    assert tos_root["next_hops"] == [
        {"kind": "kag_view", "id": "aoa-techniques"},
        {"kind": "playbook", "id": "AOA-P-0009"},
    ]

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


def test_build_is_deterministic_on_repeated_runs(tmp_path: Path) -> None:
    generated_dir = tmp_path / "generated"
    outputs_a = build_fixture_outputs()
    for filename, payload in outputs_a.items():
        write_json(generated_dir / filename, payload)
    snapshot_a = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(generated_dir.iterdir())
    }

    outputs_b = build_fixture_outputs()
    for filename, payload in outputs_b.items():
        write_json(generated_dir / filename, payload)
    snapshot_b = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(generated_dir.iterdir())
    }

    assert snapshot_a == snapshot_b


def test_build_task_to_tier_hints_reads_agents_registry_artifacts(tmp_path: Path) -> None:
    agents_root = tmp_path / "aoa-agents"
    shutil.copytree(FIXTURES_ROOT / "aoa-agents", agents_root)
    registry_path = agents_root / "generated" / "model_tier_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["model_tiers"][0]["artifact_requirement"] = "triage_packet"
    write_json(registry_path, payload)

    outputs = build_fixture_outputs(agents_root=agents_root)

    assert outputs["task_to_tier_hints.json"]["hints"][0]["output_artifact"] == "triage_packet"
