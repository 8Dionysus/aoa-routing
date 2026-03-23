from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import build_router


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"
WALKTHROUGHS = json.loads((FIXTURES_ROOT / "route_walkthroughs.json").read_text(encoding="utf-8"))[
    "walkthroughs"
]
KAG_SOURCE_LIFT_TECHNIQUE_IDS = [
    "AOA-T-0018",
    "AOA-T-0019",
    "AOA-T-0020",
    "AOA-T-0021",
    "AOA-T-0022",
]


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


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


def build_kag_source_lift_capsules() -> list[dict[str, object]]:
    return [
        {
            "id": "AOA-T-0018",
            "name": "markdown-technique-section-lift",
            "summary": "Lift stable technique markdown sections into derived section-level units while keeping the bundle markdown authoritative.",
            "one_line_intent": "Lift bounded technique sections without replacing the bundle markdown.",
            "use_when_short": "Use when section-level routing needs stable technique slices.",
            "do_not_use_short": "Do not use it to replace the source markdown as the canon.",
            "inputs_short": "A stable markdown bundle with routeable sections.",
            "outputs_short": "Bounded section-level units and routing handles.",
            "core_contract_short": "Keep markdown authoritative while exposing bounded section entrypoints.",
            "main_risk_short": "The main risk is over-lifting into a second source of truth.",
            "validation_short": "Validation checks that lifted sections stay source-traceable and bounded.",
            "technique_path": "techniques/docs/markdown-technique-section-lift/TECHNIQUE.md",
        },
        {
            "id": "AOA-T-0019",
            "name": "frontmatter-metadata-spine",
            "summary": "Treat bounded frontmatter and derived catalog outputs as a metadata spine for bundle routing without replacing markdown meaning.",
            "one_line_intent": "Expose bounded metadata for routing while leaving authored meaning in markdown.",
            "use_when_short": "Use when metadata needs to drive bundle-level routing.",
            "do_not_use_short": "Do not use it to collapse authored meaning into metadata alone.",
            "inputs_short": "Frontmatter and derived catalog surfaces for a technique bundle.",
            "outputs_short": "A stable metadata spine for bounded routing.",
            "core_contract_short": "Metadata should route to source-owned meaning without becoming the meaning.",
            "main_risk_short": "The main risk is widening metadata into surrogate doctrine.",
            "validation_short": "Validation checks that metadata stays bounded and source-traceable.",
            "technique_path": "techniques/docs/frontmatter-metadata-spine/TECHNIQUE.md",
        },
        {
            "id": "AOA-T-0020",
            "name": "evidence-note-provenance-lift",
            "summary": "Use typed evidence note kinds and note paths as bounded provenance handles in derived manifests without flattening them into a note graph.",
            "one_line_intent": "Expose bounded provenance handles without creating a note graph.",
            "use_when_short": "Use when derived manifests need direct provenance handles.",
            "do_not_use_short": "Do not use it to build open-ended provenance traversal.",
            "inputs_short": "Typed evidence notes and note paths.",
            "outputs_short": "Bounded provenance handles for derived consumers.",
            "core_contract_short": "Preserve provenance without flattening it into graph semantics.",
            "main_risk_short": "The main risk is graph-shaped overreach.",
            "validation_short": "Validation checks that provenance handles stay typed and bounded.",
            "technique_path": "techniques/docs/evidence-note-provenance-lift/TECHNIQUE.md",
        },
        {
            "id": "AOA-T-0021",
            "name": "bounded-relation-lift-for-kag",
            "summary": "Lift small typed direct relations into bounded edge hints for derived consumers without turning them into graph semantics.",
            "one_line_intent": "Expose one-hop relation hints without turning routing into a graph layer.",
            "use_when_short": "Use when a family-scoped companion view needs bounded direct relations.",
            "do_not_use_short": "Do not use it for open-ended same-kind traversal.",
            "inputs_short": "Typed direct relations already present in the source catalog.",
            "outputs_short": "Bounded relation hints for derived routing consumers.",
            "core_contract_short": "Lift only small direct relations and keep them family-scoped.",
            "main_risk_short": "The main risk is accidental graph semantics.",
            "validation_short": "Validation checks that relation hints stay one-hop and family-scoped.",
            "technique_path": "techniques/docs/bounded-relation-lift-for-kag/TECHNIQUE.md",
        },
        {
            "id": "AOA-T-0022",
            "name": "risk-and-negative-effect-lift",
            "summary": "Lift richer `Risks` language into bounded caution-oriented lookup and reuse without turning caution into metadata or scoring.",
            "one_line_intent": "Expose caution handles without promoting them into policy or scoring.",
            "use_when_short": "Use when bounded caution lookups support safe reuse.",
            "do_not_use_short": "Do not use it to turn caution into generated policy.",
            "inputs_short": "Richer risk language from source markdown.",
            "outputs_short": "Bounded caution-oriented lookup handles.",
            "core_contract_short": "Preserve caution as a bounded lookup seam, not a scoring system.",
            "main_risk_short": "The main risk is policy drift through over-structured caution surfaces.",
            "validation_short": "Validation checks that caution remains bounded and source-backed.",
            "technique_path": "techniques/docs/risk-and-negative-effect-lift/TECHNIQUE.md",
        },
    ]


def copy_fixture_roots(tmp_path: Path) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for repo_name in ("aoa-techniques", "aoa-skills", "aoa-evals", "aoa-memo", "aoa-agents"):
        target = tmp_path / repo_name
        shutil.copytree(FIXTURES_ROOT / repo_name, target)
        roots[repo_name] = target
    return roots


def augment_kag_source_lift_surfaces(techniques_root: Path) -> None:
    catalog_path = techniques_root / "generated" / "technique_catalog.min.json"
    catalog_payload = load_json(catalog_path)
    catalog_payload["techniques"].extend(build_kag_source_lift_technique_entries())
    write_json(catalog_path, catalog_payload)

    capsules_path = techniques_root / "generated" / "technique_capsules.json"
    capsules_payload = load_json(capsules_path)
    capsules_payload["techniques"].extend(build_kag_source_lift_capsules())
    write_json(capsules_path, capsules_payload)


def build_walkthrough_context(tmp_path: Path, fixture_variant: str) -> tuple[dict[str, dict[str, object]], dict[str, Path]]:
    roots = copy_fixture_roots(tmp_path)
    if fixture_variant == "kag":
        augment_kag_source_lift_surfaces(roots["aoa-techniques"])
    outputs = build_router.build_outputs(
        roots["aoa-techniques"],
        roots["aoa-skills"],
        roots["aoa-evals"],
        roots["aoa-memo"],
        roots["aoa-agents"],
    )
    return outputs, roots


def load_surface_entries(payload: dict[str, object], surface_file: str) -> list[dict[str, object]]:
    key_by_filename = {
        "aoa_router.min.json": "entries",
        "pairing_hints.min.json": "entries",
        "task_to_surface_hints.json": "hints",
        "technique_capsules.json": "techniques",
        "skill_capsules.json": "skills",
        "eval_capsules.json": "evals",
        "memory_catalog.min.json": "memo_surfaces",
        "technique_sections.full.json": "techniques",
        "skill_sections.full.json": "skills",
        "eval_sections.full.json": "evals",
        "memory_sections.full.json": "memo_surfaces",
    }
    entries = payload[key_by_filename[Path(surface_file).name]]
    assert isinstance(entries, list)
    return [entry for entry in entries if isinstance(entry, dict)]


def find_entry(entries: list[dict[str, object]], match_key: str, target_value: str) -> dict[str, object] | None:
    for entry in entries:
        if entry.get(match_key) == target_value:
            return entry
    return None


@pytest.mark.parametrize("walkthrough", WALKTHROUGHS, ids=[item["name"] for item in WALKTHROUGHS])
def test_route_walkthrough_smokes_resolve_canonical_flows(
    tmp_path: Path,
    walkthrough: dict[str, object],
) -> None:
    fixture_variant = walkthrough["fixture_variant"]
    assert isinstance(fixture_variant, str)
    outputs, roots = build_walkthrough_context(tmp_path, fixture_variant)
    hints = {hint["kind"]: hint for hint in outputs["task_to_surface_hints.json"]["hints"]}

    pick = walkthrough.get("pick")
    if isinstance(pick, dict):
        target_kind = pick["target_kind"]
        assert any(
            entry["kind"] == target_kind for entry in outputs["aoa_router.min.json"]["entries"]
        )

    inspect = walkthrough.get("inspect")
    if isinstance(inspect, dict):
        kind = inspect["kind"]
        target_value = inspect["target_value"]
        hint = hints[kind]
        inspect_action = hint["actions"]["inspect"]
        assert inspect_action["enabled"] is True
        inspect_payload = load_json(roots[hint["source_repo"]] / inspect_action["surface_file"])
        inspect_entry = find_entry(
            load_surface_entries(inspect_payload, inspect_action["surface_file"]),
            inspect_action["match_field"],
            target_value,
        )
        assert inspect_entry is not None

    expand = walkthrough.get("expand")
    if isinstance(expand, dict):
        kind = expand["kind"]
        target_value = expand["target_value"]
        section_value = expand["section_value"]
        hint = hints[kind]
        expand_action = hint["actions"]["expand"]
        assert expand_action["enabled"] is True
        expand_payload = load_json(roots[hint["source_repo"]] / expand_action["surface_file"])
        expand_entry = find_entry(
            load_surface_entries(expand_payload, expand_action["surface_file"]),
            expand_action["match_field"],
            target_value,
        )
        assert expand_entry is not None
        sections = expand_entry["sections"]
        assert isinstance(sections, list)
        assert any(
            isinstance(section, dict)
            and section.get(expand_action["section_key_field"]) == section_value
            for section in sections
        )

    pair = walkthrough.get("pair")
    if isinstance(pair, dict):
        pairing_entries = load_surface_entries(outputs["pairing_hints.min.json"], "pairing_hints.min.json")
        pair_entry = find_entry(pairing_entries, "id", pair["source_id"])
        assert pair_entry is not None
        pairs = pair_entry["pairs"]
        assert isinstance(pairs, list)
        for expected_target in pair["targets"]:
            assert expected_target in pairs
        if pair["source_kind"] == "technique":
            family_ids = set(outputs["kag_source_lift_relation_hints.min.json"]["family_ids"])
            assert pair["source_id"] in family_ids
            assert all(
                isinstance(target, dict)
                and target.get("kind") == "technique"
                and target.get("id") in family_ids
                for target in pairs
            )

    recall = walkthrough.get("recall")
    if isinstance(recall, dict):
        memo_hint = hints["memo"]
        recall_action = memo_hint["actions"]["recall"]
        assert recall_action["enabled"] is True
        mode = recall["mode"]
        assert mode in recall_action["supported_modes"]
        contract_file = recall_action["contracts_by_mode"][mode]
        contract = load_json(roots["aoa-memo"] / contract_file)
        assert contract["mode"] == mode
        assert contract["inspect_surface"] == memo_hint["actions"]["inspect"]["surface_file"]
        assert contract["expand_surface"] == memo_hint["actions"]["expand"]["surface_file"]
