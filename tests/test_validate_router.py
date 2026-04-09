from __future__ import annotations

import json
import shutil
from pathlib import Path

import build_router
import validate_router


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


def discover_workspace_root() -> Path:
    test_file = Path(__file__).resolve()
    candidates = (
        test_file.parents[1],
        test_file.parents[2],
        test_file.parents[3],
    )
    required_repos = ("Agents-of-Abyss", "Tree-of-Sophia", "Dionysus", "8Dionysus", "aoa-sdk")
    for candidate in candidates:
        if all((candidate / repo_name).exists() for repo_name in required_repos):
            return candidate
    return test_file.parents[2]


WORKSPACE_ROOT = discover_workspace_root()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def copy_repo_text(repo_root: Path, relative_path: str) -> None:
    source = Path(__file__).resolve().parents[1] / relative_path
    destination = repo_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def copy_live_repo_text(roots: dict[str, Path], repo_name: str, relative_path: str) -> None:
    source = WORKSPACE_ROOT / repo_name / relative_path
    destination = roots[repo_name] / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def ensure_placeholder_file(path: Path, *, anchor: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    suffix = path.suffix.lower()
    if suffix == ".md":
        text = "# Placeholder\n"
        if anchor:
            text = f'<a id="{anchor}"></a>\n\n# Placeholder\n'
        path.write_text(text, encoding="utf-8")
        return
    if suffix in {".yaml", ".yml"}:
        path.write_text("placeholder: true\n", encoding="utf-8")
        return
    if suffix == ".toml":
        path.write_text("[placeholder]\nenabled = true\n", encoding="utf-8")
        return
    if suffix == ".py":
        path.write_text('"""Placeholder fixture file."""\n', encoding="utf-8")
        return
    if suffix == ".json":
        path.write_text("{}\n", encoding="utf-8")
        return
    path.write_text("placeholder\n", encoding="utf-8")


def ensure_local_ref_placeholder(repo_root: Path, relative_ref: str) -> None:
    path_text, _, anchor = relative_ref.partition("#")
    ensure_placeholder_file(repo_root / path_text, anchor=anchor or None)


def ensure_repo_ref_placeholder(roots: dict[str, Path], raw_ref: str) -> None:
    repo_name, _, relative_ref = raw_ref.partition(":")
    ensure_local_ref_placeholder(roots[repo_name], relative_ref)


def hydrate_route_map_fixture(roots: dict[str, Path], repo_name: str, relative_path: str) -> None:
    copy_live_repo_text(roots, repo_name, relative_path)
    payload = json.loads((roots[repo_name] / relative_path).read_text(encoding="utf-8"))
    copy_live_repo_text(roots, repo_name, payload["schema_ref"])
    ensure_local_ref_placeholder(roots[repo_name], payload["authority_ref"])
    for ref in payload.get("validation_refs", []):
        ensure_local_ref_placeholder(roots[repo_name], ref)
    if "workspace_manifest_ref" in payload:
        ensure_local_ref_placeholder(roots[repo_name], payload["workspace_manifest_ref"])
    if "next_live_seed_ref" in payload:
        ensure_local_ref_placeholder(roots[repo_name], payload["next_live_seed_ref"])
    for route in payload["routes"]:
        if "surface_ref" in route:
            ensure_local_ref_placeholder(roots[repo_name], route["surface_ref"])
        if "capsule_ref" in route:
            ensure_repo_ref_placeholder(roots, route["capsule_ref"])
        if "authority_ref" in route:
            ensure_repo_ref_placeholder(roots, route["authority_ref"])
        for ref in route.get("verification_refs", []):
            if ":" in ref:
                ensure_repo_ref_placeholder(roots, ref)
            else:
                ensure_local_ref_placeholder(roots[repo_name], ref)


def hydrate_catalog_fixture(roots: dict[str, Path], repo_name: str, relative_path: str) -> None:
    if repo_name != "abyss-stack":
        copy_live_repo_text(roots, repo_name, relative_path)
    payload = json.loads((roots[repo_name] / relative_path).read_text(encoding="utf-8"))
    schema_ref = payload.get("schema_ref")
    if repo_name != "abyss-stack" and isinstance(schema_ref, str):
        copy_live_repo_text(roots, repo_name, schema_ref)
    authority_ref = payload.get("authority_ref")
    if isinstance(authority_ref, str):
        ensure_local_ref_placeholder(roots[repo_name], authority_ref)
    for ref in payload.get("validation_refs", []):
        ensure_local_ref_placeholder(roots[repo_name], ref)
    for entry in payload.get("surfaces", []):
        for key in ("schema_ref", "surface_ref", "path", "example_ref"):
            ref = entry.get(key)
            if isinstance(ref, str):
                ensure_local_ref_placeholder(roots[repo_name], ref)


def hydrate_capsule_fixture_roots(roots: dict[str, Path]) -> None:
    hydrate_route_map_fixture(roots, "Agents-of-Abyss", "generated/center_entry_map.min.json")
    hydrate_route_map_fixture(roots, "Tree-of-Sophia", "generated/root_entry_map.min.json")
    hydrate_route_map_fixture(roots, "aoa-sdk", "generated/workspace_control_plane.min.json")
    hydrate_route_map_fixture(roots, "Dionysus", "generated/seed_route_map.min.json")
    hydrate_route_map_fixture(roots, "8Dionysus", "generated/public_route_map.min.json")
    hydrate_catalog_fixture(roots, "aoa-stats", "generated/summary_surface_catalog.min.json")
    hydrate_catalog_fixture(roots, "abyss-stack", "generated/diagnostic_surface_catalog.min.json")


def copy_fixture_roots(tmp_path: Path) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for repo_name in FIXTURE_REPO_NAMES:
        target = tmp_path / repo_name
        shutil.copytree(FIXTURES_ROOT / repo_name, target)
        roots[repo_name] = target
    hydrate_capsule_fixture_roots(roots)
    return roots


def build_outputs_from_roots(roots: dict[str, Path]) -> dict[str, dict[str, object]]:
    return build_router.build_outputs(
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


def build_fixture_generated(
    tmp_path: Path,
    *,
    generated_dir_name: str = "generated",
) -> tuple[Path, dict[str, Path]]:
    roots = copy_fixture_roots(tmp_path)
    generated_dir = tmp_path / generated_dir_name
    outputs = build_outputs_from_roots(roots)
    for filename, payload in outputs.items():
        write_output(generated_dir / filename, payload)
    return generated_dir, roots


def validate_fixture_generated(generated_dir: Path, roots: dict[str, Path]) -> list[validate_router.ValidationIssue]:
    return validate_router.validate_generated_outputs(
        generated_dir,
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


def test_validate_generated_outputs_accepts_fixture_build(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    issues = validate_fixture_generated(generated_dir, roots)
    assert issues == []


def test_validate_local_questbook_surfaces_accepts_foundation_files(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(
        repo_root / "QUESTBOOK.md",
        "\n".join(
            (
                "# QUESTBOOK.md — aoa-routing",
                "",
                "## Frontier",
                "",
                "- none right now",
                "",
                "## Near",
                "",
                "- none right now",
                "",
                "## Blocked / reanchor",
                "",
                "- `AOA-RT-Q-0002`",
                "",
            )
        ),
    )
    write_text(
        repo_root / "docs" / "QUEST_ROUTING_SEAM.md",
        "\n".join(validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS) + "\n",
    )
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": ["schema_version", "id", "repo", "state", "band", "difficulty", "risk", "delegate_tier", "source_path", "public_safe", "next_actions", "fallback"],
            "properties": {
                "schema_version": {"const": "quest_dispatch_hint_v2"},
                "id": {"type": "string"},
                "repo": {"type": "string"},
                "state": {"type": "string"},
                "band": {"type": "string"},
                "difficulty": {"type": "string"},
                "risk": {"type": "string"},
                "delegate_tier": {"type": "string"},
                "source_path": {"type": "string"},
                "public_safe": {"type": "boolean"},
                "next_actions": {"type": "array"},
                "fallback": {"type": "object"},
            },
        },
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0001.yaml",
        "\n".join(
            (
                "schema_version: work_quest_v1",
                "id: AOA-RT-Q-0001",
                "repo: aoa-routing",
                "state: done",
                "public_safe: true",
            )
        )
        + "\n",
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0002.yaml",
        "\n".join(
            (
                "schema_version: work_quest_v1",
                "id: AOA-RT-Q-0002",
                "repo: aoa-routing",
                "state: reanchor",
                "notes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"",
                "public_safe: true",
            )
        )
        + "\n",
    )

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert issues == []


def test_validate_local_questbook_surfaces_accepts_additive_quest_board_files(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(
        repo_root / "QUESTBOOK.md",
        "\n".join(
            (
                "# QUESTBOOK.md — aoa-routing",
                "",
                "## Frontier",
                "",
                "- none right now",
                "",
                "## Near",
                "",
                "- `AOA-RT-Q-0003`",
                "",
                "## Blocked / reanchor",
                "",
                "- `AOA-RT-Q-0002`",
                "",
            )
        ),
    )
    write_text(
        repo_root / "docs" / "QUEST_ROUTING_SEAM.md",
        "\n".join(validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS) + "\n",
    )
    write_text(
        repo_root / "docs" / "QUEST_BOARD_SEAM.md",
        "# Quest Board Seam\n\nExample-only.\n",
    )
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": ["schema_version", "id", "repo", "state", "band", "difficulty", "risk", "delegate_tier", "source_path", "public_safe", "next_actions", "fallback"],
            "properties": {
                "schema_version": {"const": "quest_dispatch_hint_v2"},
                "id": {"type": "string"},
                "repo": {"type": "string"},
                "state": {"type": "string"},
                "band": {"type": "string"},
                "difficulty": {"type": "string"},
                "risk": {"type": "string"},
                "delegate_tier": {"type": "string"},
                "source_path": {"type": "string"},
                "public_safe": {"type": "boolean"},
                "next_actions": {"type": "array"},
                "fallback": {"type": "object"},
            },
        },
    )
    write_json(
        repo_root / "schemas" / "quest_board_entry.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_board_entry_v1.schema.json",
            "title": "quest_board_entry_v1",
            "type": "object",
            "additionalProperties": False,
            "required": [
                "schema_version",
                "id",
                "title",
                "repo",
                "state",
                "band",
                "difficulty",
                "risk",
                "control_mode",
                "delegate_tier",
                "source_dispatch_ref",
                "entry_actions",
                "recommended_party",
                "progression_gate",
                "public_safe",
            ],
            "properties": {
                "schema_version": {"const": "quest_board_entry_v1"},
                "id": {"type": "string"},
                "title": {"type": "string"},
                "repo": {"type": "string"},
                "state": {"type": "string"},
                "band": {"type": "string"},
                "difficulty": {"type": "string"},
                "risk": {"type": "string"},
                "control_mode": {"type": "string"},
                "delegate_tier": {"type": "string"},
                "source_dispatch_ref": {"type": "string"},
                "entry_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "recommended_party": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["cohort_pattern", "roles", "tier_path"],
                    "properties": {
                        "cohort_pattern": {"type": "string"},
                        "roles": {"type": "array", "items": {"type": "string"}},
                        "tier_path": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "progression_gate": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["min_rank", "preferred_axes", "note"],
                    "properties": {
                        "min_rank": {"type": "string"},
                        "preferred_axes": {"type": "array", "items": {"type": "string"}},
                        "note": {"type": "string"},
                    },
                },
                "public_safe": {"type": "boolean"},
            },
        },
    )
    write_json(
        repo_root / "generated" / "quest_board.min.example.json",
        {
            "version": 1,
            "authority": "derived-example-only",
            "wave_scope": "adjunct-rpg-first-wave",
            "inputs": [
                {"repo": "aoa-skills", "surface_kind": "quest_dispatch", "ref": "generated/quest_dispatch.min.json"},
                {"repo": "aoa-agents", "surface_kind": "agent_progression_example", "ref": "examples/agent_progression.example.json"},
                {"repo": "aoa-evals", "surface_kind": "progression_evidence_example", "ref": "examples/progression_evidence.example.json"},
            ],
            "entries": [
                {
                    "schema_version": "quest_board_entry_v1",
                    "id": "AOA-SK-Q-0003",
                    "title": "Portable-layer contract hardening",
                    "repo": "aoa-skills",
                    "state": "triaged",
                    "band": "frontier",
                    "difficulty": "d3_seam",
                    "risk": "r2_contract",
                    "control_mode": "human_codex_copilot",
                    "delegate_tier": "planner",
                    "source_dispatch_ref": "generated/quest_dispatch.min.json#AOA-SK-Q-0003",
                    "entry_actions": ["inspect", "expand", "handoff"],
                    "recommended_party": {
                        "cohort_pattern": "pair",
                        "roles": ["architect", "coder", "reviewer"],
                        "tier_path": ["planner", "executor", "verifier"],
                    },
                    "progression_gate": {
                        "min_rank": "adept",
                        "preferred_axes": ["boundary_integrity"],
                        "note": "Derived hint only.",
                    },
                    "public_safe": True,
                }
            ],
        },
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0001.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0001\nrepo: aoa-routing\nstate: done\npublic_safe: true\n",
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0002.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0002\nrepo: aoa-routing\nstate: reanchor\nnotes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"\npublic_safe: true\n",
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0003.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0003\nrepo: aoa-routing\nstate: captured\npublic_safe: true\n",
    )

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert issues == []


def test_validate_local_questbook_surfaces_accepts_rpg_navigation_bridge_files(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(
        repo_root / "QUESTBOOK.md",
        "\n".join(
            (
                "# QUESTBOOK.md — aoa-routing",
                "",
                "## Frontier",
                "",
                "- `AOA-RT-Q-0004`",
                "",
                "## Near",
                "",
                "- none yet",
                "",
                "## Blocked / reanchor",
                "",
                "- `AOA-RT-Q-0002`",
                "",
            )
        ),
    )
    write_text(
        repo_root / "docs" / "QUEST_ROUTING_SEAM.md",
        "\n".join(validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS) + "\n",
    )
    copy_repo_text(repo_root, "docs/RPG_NAVIGATION_BRIDGE.md")
    copy_repo_text(repo_root, "schemas/rpg_navigation_bundle.schema.json")
    copy_repo_text(repo_root, "generated/rpg_navigation.min.example.json")
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": [],
            "properties": {"schema_version": {"const": "quest_dispatch_hint_v2"}},
        },
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0001.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0001\nrepo: aoa-routing\nstate: done\npublic_safe: true\n",
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0002.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0002\nrepo: aoa-routing\nstate: reanchor\nnotes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"\npublic_safe: true\n",
    )
    copy_repo_text(repo_root, "quests/AOA-RT-Q-0004.yaml")

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert issues == []


def test_validate_local_questbook_surfaces_rejects_legacy_rpg_navigation_input_repo(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(
        repo_root / "QUESTBOOK.md",
        "\n".join(
            (
                "# QUESTBOOK.md — aoa-routing",
                "",
                "## Frontier",
                "",
                "- `AOA-RT-Q-0004`",
                "",
                "## Near",
                "",
                "- none yet",
                "",
                "## Blocked / reanchor",
                "",
                "- `AOA-RT-Q-0002`",
                "",
            )
        ),
    )
    write_text(
        repo_root / "docs" / "QUEST_ROUTING_SEAM.md",
        "\n".join(validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS) + "\n",
    )
    copy_repo_text(repo_root, "docs/RPG_NAVIGATION_BRIDGE.md")
    copy_repo_text(repo_root, "schemas/rpg_navigation_bundle.schema.json")
    navigation_payload = json.loads(
        (Path(__file__).resolve().parents[1] / "generated" / "rpg_navigation.min.example.json").read_text(
            encoding="utf-8"
        )
    )
    navigation_payload["inputs"][0]["repo"] = "aoa-routing"
    write_json(repo_root / "generated" / "rpg_navigation.min.example.json", navigation_payload)
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": [],
            "properties": {"schema_version": {"const": "quest_dispatch_hint_v2"}},
        },
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0001.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0001\nrepo: aoa-routing\nstate: done\npublic_safe: true\n",
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0002.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0002\nrepo: aoa-routing\nstate: reanchor\nnotes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"\npublic_safe: true\n",
    )
    copy_repo_text(repo_root, "quests/AOA-RT-Q-0004.yaml")

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert any("must not pretend aoa-routing owns quest_dispatch" in issue.message for issue in issues)


def test_validate_local_questbook_surfaces_ignores_quest_dispatch_text_outside_inputs(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(
        repo_root / "QUESTBOOK.md",
        "\n".join(
            (
                "# QUESTBOOK.md — aoa-routing",
                "",
                "## Frontier",
                "",
                "- `AOA-RT-Q-0004`",
                "",
                "## Near",
                "",
                "- none yet",
                "",
                "## Blocked / reanchor",
                "",
                "- `AOA-RT-Q-0002`",
                "",
            )
        ),
    )
    write_text(
        repo_root / "docs" / "QUEST_ROUTING_SEAM.md",
        "\n".join(validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS) + "\n",
    )
    copy_repo_text(repo_root, "docs/RPG_NAVIGATION_BRIDGE.md")
    navigation_payload = json.loads(
        (Path(__file__).resolve().parents[1] / "generated" / "rpg_navigation.min.example.json").read_text(
            encoding="utf-8"
        )
    )
    navigation_payload["notes"] = (
        f"{navigation_payload['notes']} "
        'Example anti-pattern text: {"repo": "aoa-routing", "surface_kind": "quest_dispatch"}.'
    )
    write_json(repo_root / "generated" / "rpg_navigation.min.example.json", navigation_payload)
    copy_repo_text(repo_root, "schemas/rpg_navigation_bundle.schema.json")
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": [],
            "properties": {"schema_version": {"const": "quest_dispatch_hint_v2"}},
        },
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0001.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0001\nrepo: aoa-routing\nstate: done\npublic_safe: true\n",
    )
    write_text(
        repo_root / "quests" / "AOA-RT-Q-0002.yaml",
        "schema_version: work_quest_v1\nid: AOA-RT-Q-0002\nrepo: aoa-routing\nstate: reanchor\nnotes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"\npublic_safe: true\n",
    )
    copy_repo_text(repo_root, "quests/AOA-RT-Q-0004.yaml")

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert issues == []


def test_validate_local_questbook_surfaces_rejects_wrong_repo(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(repo_root / "QUESTBOOK.md", "## Blocked / reanchor\n\n- `AOA-RT-Q-0002`\n")
    write_text(repo_root / "docs" / "QUEST_ROUTING_SEAM.md", "\n".join(validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS) + "\n")
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": [],
            "properties": {"schema_version": {"const": "quest_dispatch_hint_v2"}},
        },
    )
    write_text(repo_root / "quests" / "AOA-RT-Q-0001.yaml", "schema_version: work_quest_v1\nid: AOA-RT-Q-0001\nrepo: aoa-routing\nstate: done\npublic_safe: true\n")
    write_text(repo_root / "quests" / "AOA-RT-Q-0002.yaml", "schema_version: work_quest_v1\nid: AOA-RT-Q-0002\nrepo: aoa-playbooks\nstate: reanchor\nnotes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"\npublic_safe: true\n")

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert any("quest must target repo 'aoa-routing'" in issue.message for issue in issues)


def test_validate_local_questbook_surfaces_rejects_missing_foundation_quest(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(repo_root / "QUESTBOOK.md", "## Near\n\n- `AOA-RT-Q-0003`\n\n## Blocked / reanchor\n\n- `AOA-RT-Q-0002`\n")
    write_text(repo_root / "docs" / "QUEST_ROUTING_SEAM.md", "\n".join(validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS) + "\n")
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": [],
            "properties": {"schema_version": {"const": "quest_dispatch_hint_v2"}},
        },
    )
    write_text(repo_root / "quests" / "AOA-RT-Q-0002.yaml", "schema_version: work_quest_v1\nid: AOA-RT-Q-0002\nrepo: aoa-routing\nstate: reanchor\nnotes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"\npublic_safe: true\n")

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert any("foundation quests" in issue.message and "AOA-RT-Q-0001" in issue.message for issue in issues)


def test_validate_local_questbook_surfaces_rejects_missing_live_parsing_refusal(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(repo_root / "QUESTBOOK.md", "## Blocked / reanchor\n\n- `AOA-RT-Q-0002`\n")
    write_text(
        repo_root / "docs" / "QUEST_ROUTING_SEAM.md",
        "\n".join(snippet for snippet in validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS if "parse live" not in snippet) + "\n",
    )
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": [],
            "properties": {"schema_version": {"const": "quest_dispatch_hint_v2"}},
        },
    )
    write_text(repo_root / "quests" / "AOA-RT-Q-0001.yaml", "schema_version: work_quest_v1\nid: AOA-RT-Q-0001\nrepo: aoa-routing\nstate: done\npublic_safe: true\n")
    write_text(repo_root / "quests" / "AOA-RT-Q-0002.yaml", "schema_version: work_quest_v1\nid: AOA-RT-Q-0002\nrepo: aoa-routing\nstate: reanchor\nnotes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"\npublic_safe: true\n")

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert any("generated-only ingestion" in issue.message for issue in issues)


def test_validate_local_questbook_surfaces_reports_non_mapping_schema_properties(tmp_path: Path) -> None:
    repo_root = tmp_path / "aoa-routing"
    issues: list[validate_router.ValidationIssue] = []
    write_text(repo_root / "QUESTBOOK.md", "## Blocked / reanchor\n\n- `AOA-RT-Q-0002`\n")
    write_text(
        repo_root / "docs" / "QUEST_ROUTING_SEAM.md",
        "\n".join(validate_router.REQUIRED_ROUTING_SEAM_SNIPPETS) + "\n",
    )
    write_json(
        repo_root / "schemas" / "quest_dispatch_hint.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://8dionysus.github.io/schemas/quest_dispatch_hint_v2.schema.json",
            "title": "quest_dispatch_hint_v2",
            "type": "object",
            "additionalProperties": False,
            "required": [],
            "properties": [],
        },
    )
    write_text(repo_root / "quests" / "AOA-RT-Q-0001.yaml", "schema_version: work_quest_v1\nid: AOA-RT-Q-0001\nrepo: aoa-routing\nstate: done\npublic_safe: true\n")
    write_text(repo_root / "quests" / "AOA-RT-Q-0002.yaml", "schema_version: work_quest_v1\nid: AOA-RT-Q-0002\nrepo: aoa-routing\nstate: reanchor\nnotes: \"reanchor: no live frontier + d0/d1 + r0/r1 source/proof quest leaves currently exist\"\npublic_safe: true\n")

    validate_router.validate_local_questbook_surfaces(repo_root, issues)

    assert any(
        issue.location == "schemas/quest_dispatch_hint.schema.json"
        and "must be a mapping" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_accepts_custom_generated_dir(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path, generated_dir_name="custom-output")
    issues = validate_fixture_generated(generated_dir, roots)
    assert issues == []


def test_validate_generated_outputs_keeps_fixture_bytes_stable(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    before = {path.name: path.read_bytes() for path in generated_dir.iterdir() if path.is_file()}

    issues = validate_fixture_generated(generated_dir, roots)

    after = {path.name: path.read_bytes() for path in generated_dir.iterdir() if path.is_file()}
    assert issues == []
    assert before == after


def test_validate_generated_outputs_rejects_missing_live_quest_dispatch_surface(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    (roots["aoa-skills"] / "generated" / "quest_dispatch.min.json").unlink()

    issues = validate_fixture_generated(generated_dir, roots)

    assert any("quest_dispatch.min.json is missing" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_missing_live_quest_catalog_surface(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    (roots["aoa-techniques"] / "generated" / "quest_catalog.min.json").unlink()

    issues = validate_fixture_generated(generated_dir, roots)

    assert any("quest_catalog.min.json is missing" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_example_backed_quest_input(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    live_path = roots["aoa-evals"] / "generated" / "quest_dispatch.min.json"
    example_path = roots["aoa-evals"] / "generated" / "quest_dispatch.min.example.json"
    example_path.write_text(live_path.read_text(encoding="utf-8"), encoding="utf-8")
    live_path.unlink()

    issues = validate_fixture_generated(generated_dir, roots)

    assert any("quest_dispatch.min.json is missing" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_closed_quest_in_live_routing_hints(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "quest_dispatch_hints.min.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    payload["hints"].append(
        {
            "schema_version": "quest_dispatch_hint_v2",
            "id": "AOA-TECH-Q-0001",
            "repo": "aoa-techniques",
            "state": "done",
            "band": "frontier",
            "difficulty": "d2_slice",
            "risk": "r1_repo_local",
            "delegate_tier": "executor",
            "source_path": "quests/AOA-TECH-Q-0001.yaml",
            "public_safe": True,
            "next_actions": [
                {
                    "verb": "inspect",
                    "target_repo": "aoa-techniques",
                    "target_surface": "generated/quest_dispatch.min.json",
                    "match_key": "id",
                    "target_value": "AOA-TECH-Q-0001",
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
                    "target_value": "executor",
                },
            ],
            "fallback": {
                "verb": "inspect",
                "target_repo": "aoa-techniques",
                "target_surface": "generated/quest_catalog.min.json",
                "match_key": "id",
                "target_value": "AOA-TECH-Q-0001",
            },
        }
    )
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)

    assert any("must not include closed quests" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_quest_hint_action_order_drift(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "quest_dispatch_hints.min.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    payload["hints"][0]["next_actions"][0], payload["hints"][0]["next_actions"][1] = (
        payload["hints"][0]["next_actions"][1],
        payload["hints"][0]["next_actions"][0],
    )
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)

    assert any(".next_actions[0].verb must stay 'inspect'" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_wrong_quest_hint_handoff_tier(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "quest_dispatch_hints.min.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    payload["hints"][0]["next_actions"][2]["target_value"] = "missing-tier"
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)

    assert any("references unknown federation tier 'missing-tier'" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_wrong_quest_hint_expand_path(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "quest_dispatch_hints.min.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    payload["hints"][0]["next_actions"][1]["target_surface"] = "docs/WRONG.md"
    payload["hints"][0]["next_actions"][1]["target_value"] = "docs/WRONG.md"
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)

    assert any("must expand to the repo-local quest integration note" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_dionysus_quest_in_first_live_wave(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "quest_dispatch_hints.min.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    payload["hints"][0]["repo"] = "Dionysus"
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)

    assert any("first live source-only wave" in issue.message for issue in issues)


def test_validate_generated_outputs_rejects_tiny_safe_leaf_while_rt_q_0002_is_reanchored(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    catalog_path = roots["aoa-skills"] / "generated" / "quest_catalog.min.json"
    dispatch_path = roots["aoa-skills"] / "generated" / "quest_dispatch.min.json"
    catalog_payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    dispatch_payload = json.loads(dispatch_path.read_text(encoding="utf-8"))
    for entry in catalog_payload:
        if entry["id"] == "AOA-SK-Q-0003":
            entry["difficulty"] = "d1_patch"
            entry["risk"] = "r1_repo_local"
            break
    for entry in dispatch_payload:
        if entry["id"] == "AOA-SK-Q-0003":
            entry["difficulty"] = "d1_patch"
            entry["risk"] = "r1_repo_local"
            break
    write_json(catalog_path, catalog_payload)
    write_json(dispatch_path, dispatch_payload)
    outputs = build_outputs_from_roots(roots)
    for filename, payload in outputs.items():
        write_output(generated_dir / filename, payload)

    issues = validate_fixture_generated(generated_dir, roots)

    assert any("must not remain reanchored once live frontier d0/d1 r0/r1 leaves exist" in issue.message for issue in issues)


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


def test_validate_generated_outputs_rejects_two_stage_schema_drift_via_schema(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tool_schemas_path = generated_dir / "two_stage_router_tool_schemas.json"
    payload = json.loads(tool_schemas_path.read_text(encoding="utf-8"))
    del payload["tools"]
    write_json(tool_schemas_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "two_stage_router_tool_schemas.json"
        and "schema violation" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_source_owned_field_leak_in_two_stage_prompt_blocks(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    prompt_blocks_path = generated_dir / "two_stage_router_prompt_blocks.json"
    payload = json.loads(prompt_blocks_path.read_text(encoding="utf-8"))
    payload["tiny_preselector_system"] += " Never copy summary fields."
    write_json(prompt_blocks_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "two_stage_router_prompt_blocks.json"
        and "source-owned payload field" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_source_owned_field_in_two_stage_tool_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tool_schemas_path = generated_dir / "two_stage_router_tool_schemas.json"
    payload = json.loads(tool_schemas_path.read_text(encoding="utf-8"))
    payload["tools"][0]["input_schema"]["properties"]["summary"] = {"type": "string"}
    write_json(tool_schemas_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "two_stage_router_tool_schemas.json"
        and "must not expose source-owned payload fields" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_stale_two_stage_manifest_against_rebuild(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    manifest_path = generated_dir / "two_stage_router_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["integration_mode"] = "stale-seam"
    write_json(manifest_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "two_stage_router_manifest.json"
        and "canonical rebuild from current sibling catalogs" in issue.message
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


def test_validate_generated_outputs_rejects_malformed_technique_second_cut_action_via_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    del payload["hints"][0]["actions"]["second_cut"]["selection_axis"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        ("schema violation" in issue.message and "actions.second_cut" in issue.message)
        or "selection_axis" in issue.message
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


def test_validate_generated_outputs_rejects_malformed_parallel_recall_family_via_schema(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    del memo_hint["actions"]["recall"]["parallel_families"]["memory_objects"]["inspect_surface"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        ("schema violation" in issue.message and "parallel_families" in issue.message)
        or "inspect_surface" in issue.message
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


def test_validate_generated_outputs_rejects_missing_technique_second_cut_target(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    (roots["aoa-techniques"] / "generated" / "technique_kind_manifest.min.json").unlink()

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "aoa-techniques/generated/technique_kind_manifest.min.json"
        and "is missing" in issue.message
        for issue in issues
    )


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


def test_validate_generated_outputs_rejects_missing_memo_capsule_mode_mapping(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    del memo_hint["actions"]["recall"]["capsule_surfaces_by_mode"]["semantic"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "memo capsule_surfaces_by_mode must include mode 'semantic'" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_memo_capsule_surface_mismatch(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    memo_hint["actions"]["recall"]["capsule_surfaces_by_mode"]["semantic"] = (
        "generated/memory_object_capsules.json"
    )
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "recall contract capsule_surface must match memo capsule_surfaces_by_mode for mode 'semantic'"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_missing_memo_capsule_surface_target(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    memo_hint["actions"]["recall"]["capsule_surfaces_by_mode"]["semantic"] = (
        "generated/missing_memory_capsules.json"
    )
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "aoa-memo/generated/missing_memory_capsules.json"
        and "is missing" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_non_string_recall_contract_path_without_crashing(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    memo_hint["actions"]["recall"]["contracts_by_mode"]["semantic"] = ["bad-contract-path"]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "task_to_surface_hints.json.memo.actions.recall.contracts_by_mode.semantic must be a non-empty string"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_missing_parallel_object_recall_contract(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    (roots["aoa-memo"] / "examples" / "recall_contract.object.semantic.json").unlink()

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "aoa-memo/examples/recall_contract.object.semantic.json" == issue.location
        and "is missing" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_parallel_object_contract_surface_mismatch(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    contract_path = roots["aoa-memo"] / "examples" / "recall_contract.object.semantic.json"
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    payload["expand_surface"] = "generated/memory_sections.full.json"
    write_json(contract_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "parallel recall family 'memory_objects' contract expand_surface must match the family expand surface"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_missing_parallel_object_capsule_mode_mapping(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    del memo_hint["actions"]["recall"]["parallel_families"]["memory_objects"]["capsule_surfaces_by_mode"][
        "semantic"
    ]
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "parallel recall family 'memory_objects' capsule_surfaces_by_mode must include mode 'semantic'"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_parallel_object_capsule_surface_mismatch(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    memo_hint["actions"]["recall"]["parallel_families"]["memory_objects"]["capsule_surfaces_by_mode"][
        "semantic"
    ] = "generated/memory_capsules.json"
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "parallel recall family 'memory_objects' contract capsule_surface must match capsule_surfaces_by_mode for mode 'semantic'"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_parallel_object_contract_absolute_path(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    hints_path = generated_dir / "task_to_surface_hints.json"
    payload = json.loads(hints_path.read_text(encoding="utf-8"))
    memo_hint = next(hint for hint in payload["hints"] if hint["kind"] == "memo")
    memo_hint["actions"]["recall"]["parallel_families"]["memory_objects"]["contracts_by_mode"][
        "semantic"
    ] = "/tmp/escape.json"
    write_json(hints_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "task_to_surface_hints.json.memo.actions.recall.parallel_families.memory_objects.contracts_by_mode.semantic must be repo-relative, not absolute"
        in issue.message
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


def test_validate_generated_outputs_rejects_tiny_model_recall_query_unknown_family(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"
    payload = json.loads(tiny_model_path.read_text(encoding="utf-8"))
    recall_query = next(
        query
        for query in payload["queries"]
        if query["verb"] == "recall" and query.get("recall_family") == "memory_objects"
    )
    recall_query["recall_family"] = "ghost-family"
    write_json(tiny_model_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must target a published recall family 'ghost-family'" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tiny_model_recall_starter_unknown_family(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"
    payload = json.loads(tiny_model_path.read_text(encoding="utf-8"))
    recall_starter = next(
        starter
        for starter in payload["starters"]
        if starter["verb"] == "recall" and starter.get("recall_family") == "memory_objects"
    )
    recall_starter["recall_family"] = "ghost-family"
    write_json(tiny_model_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must target a published recall family 'ghost-family'" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_federation_authority_surface_owned_by_routing(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    federation_path = generated_dir / "federation_entrypoints.min.json"
    payload = json.loads(federation_path.read_text(encoding="utf-8"))
    payload["root_entries"][0]["authority_surface"] = "aoa-routing:generated/aoa_router.min.json"
    write_json(federation_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must not point authority at aoa-routing/generated/*" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_federation_entry_missing_risk(tmp_path: Path) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    federation_path = generated_dir / "federation_entrypoints.min.json"
    payload = json.loads(federation_path.read_text(encoding="utf-8"))
    del payload["entrypoints"][0]["risk"]
    write_json(federation_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and "risk" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_declared_kind_in_federation_entrypoints(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    federation_path = generated_dir / "federation_entrypoints.min.json"
    payload = json.loads(federation_path.read_text(encoding="utf-8"))
    payload["entrypoints"][0]["kind"] = "tos_node"
    write_json(federation_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and "tos_node" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_route_map_capsule_implementation_ref(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    capsule_path = roots["aoa-sdk"] / "generated" / "workspace_control_plane.min.json"
    payload = json.loads(capsule_path.read_text(encoding="utf-8"))
    payload["routes"][0]["verification_refs"][0] = "src/aoa_sdk/workspace/discovery.py"
    write_json(capsule_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must not point to implementation path" in issue.message
        and "src/aoa_sdk/workspace/discovery.py" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_public_route_map_implementation_ref(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    capsule_path = roots["8Dionysus"] / "generated" / "public_route_map.min.json"
    payload = json.loads(capsule_path.read_text(encoding="utf-8"))
    payload["routes"][0]["capsule_ref"] = "8Dionysus:scripts/validate_public_route_map.py"
    write_json(capsule_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must not point to implementation path" in issue.message
        and "8Dionysus:scripts/validate_public_route_map.py" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_route_map_schema_version_drift(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    capsule_path = roots["aoa-sdk"] / "generated" / "workspace_control_plane.min.json"
    payload = json.loads(capsule_path.read_text(encoding="utf-8"))
    payload["schema_version"] = "aoa_sdk_workspace_control_plane_v1"
    write_json(capsule_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and "aoa_sdk_workspace_control_plane_v2" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_declared_kind_in_federation_starters(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    tiny_model_path = generated_dir / "tiny_model_entrypoints.json"
    payload = json.loads(tiny_model_path.read_text(encoding="utf-8"))
    for starter in payload["federation_starters"]:
        if starter["name"] == "agent-root":
            starter["entry_kind"] = "tos_node"
            break
    write_json(tiny_model_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must not target a declared-but-inactive entry kind" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_unbounded_federation_root_fanout(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    federation_path = generated_dir / "federation_entrypoints.min.json"
    payload = json.loads(federation_path.read_text(encoding="utf-8"))
    payload["root_entries"][0]["next_actions"].append(
        {
            "verb": "inspect",
            "target_repo": "aoa-routing",
            "target_surface": "generated/federation_entrypoints.min.json",
            "match_key": "id",
            "target_value": "AOA-A-0001",
        }
    )
    write_json(federation_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "schema violation" in issue.message and "next_actions" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tos_tiny_entry_route_boundary_drift(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    route_path = roots["Tree-of-Sophia"] / "examples" / "tos_tiny_entry_route.example.json"
    payload = json.loads(route_path.read_text(encoding="utf-8"))
    payload["fallback"] = "aoa-routing/generated/aoa_router.min.json"
    write_json(route_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must stay inside Tree-of-Sophia and must not point at downstream repos" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tos_tiny_entry_route_id_drift(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    route_path = roots["Tree-of-Sophia"] / "examples" / "tos_tiny_entry_route.example.json"
    payload = json.loads(route_path.read_text(encoding="utf-8"))
    payload["route_id"] = "tos-tiny-entry.drifted"
    write_json(route_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "route_id must stay 'tos-tiny-entry.zarathustra-prologue'" in issue.message
        or "target 'tos-tiny-entry.zarathustra-prologue' was not found" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tos_kag_view_entry_surface_drift(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    spine_path = roots["aoa-kag"] / "generated" / "federation_spine.min.json"
    payload = json.loads(spine_path.read_text(encoding="utf-8"))
    payload["repos"][1]["current_entry_surface_refs"] = ["Tree-of-Sophia/README.md"]
    write_json(spine_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "current_entry_surface_refs must stay" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tos_kag_view_route_id_drift(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    spine_path = roots["aoa-kag"] / "generated" / "federation_spine.min.json"
    payload = json.loads(spine_path.read_text(encoding="utf-8"))
    payload["repos"][1]["example_object_ids"] = ["tos-tiny-entry.drifted"]
    write_json(spine_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "example_object_ids must stay ['tos-tiny-entry.zarathustra-prologue']" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tos_kag_view_adjunct_drift(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    spine_path = roots["aoa-kag"] / "generated" / "federation_spine.min.json"
    payload = json.loads(spine_path.read_text(encoding="utf-8"))
    payload["repos"][1]["adjunct_surfaces"][0]["target_value"] = "AOA-K-0011::drifted"
    write_json(spine_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "adjunct_surfaces must publish exactly the bounded AOA-K-0011 adjunct" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_wrong_memo_return_primary_target(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    return_path = generated_dir / "return_navigation_hints.min.json"
    payload = json.loads(return_path.read_text(encoding="utf-8"))
    memo_return = next(
        record for record in payload["thin_router_returns"] if record["context_kind"] == "memo"
    )
    memo_return["primary_action"]["target_surface"] = "examples/recall_contract.object.working.json"
    write_json(return_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "memo return primary_action must point to aoa-memo/examples/recall_contract.object.working.return.json"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_memo_return_contract_without_capsule_surface(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    contract_path = (
        roots["aoa-memo"] / "examples" / "recall_contract.object.working.return.json"
    )
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    payload.pop("capsule_surface", None)
    write_json(contract_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "aoa-memo/examples/recall_contract.object.working.return.json is missing required keys: capsule_surface"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_thin_router_return_with_router_owned_fallback(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    return_path = generated_dir / "return_navigation_hints.min.json"
    payload = json.loads(return_path.read_text(encoding="utf-8"))
    technique_return = next(
        record for record in payload["thin_router_returns"] if record["context_kind"] == "technique"
    )
    technique_return["secondary_action"] = {
        "verb": "inspect",
        "target_repo": "aoa-routing",
        "target_surface": "generated/federation_entrypoints.min.json",
        "match_field": "kind",
        "target_value": "technique",
    }
    write_json(return_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must not point primary authority or thin-router re-entry at aoa-routing" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_federation_root_primary_target_away_from_owner(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    return_path = generated_dir / "return_navigation_hints.min.json"
    payload = json.loads(return_path.read_text(encoding="utf-8"))
    aoa_root_return = next(
        record for record in payload["federation_root_returns"] if record["root_id"] == "aoa-root"
    )
    aoa_root_return["primary_action"]["target_repo"] = "Tree-of-Sophia"
    aoa_root_return["primary_action"]["target_surface"] = "CHARTER.md"
    write_json(return_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "primary_action.target_repo must equal owner_repo 'Agents-of-Abyss'" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_tos_root_secondary_reentry_drift(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    return_path = generated_dir / "return_navigation_hints.min.json"
    payload = json.loads(return_path.read_text(encoding="utf-8"))
    tos_root_return = next(
        record for record in payload["federation_root_returns"] if record["root_id"] == "tos-root"
    )
    tos_root_return["secondary_action"]["target_surface"] = "docs/TINY_ENTRY_ROUTE.md"
    write_json(return_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "secondary_action.target_surface must stay 'examples/tos_tiny_entry_route.example.json'"
        in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_router_owned_primary_return_target(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    return_path = generated_dir / "return_navigation_hints.min.json"
    payload = json.loads(return_path.read_text(encoding="utf-8"))
    playbook_return = next(
        record for record in payload["federation_kind_returns"] if record["entry_kind"] == "playbook"
    )
    playbook_return["primary_action"]["target_repo"] = "aoa-routing"
    playbook_return["primary_action"]["target_surface"] = "generated/federation_entrypoints.min.json"
    playbook_return["primary_action"]["match_field"] = "kind"
    playbook_return["primary_action"]["target_value"] = "playbook"
    write_json(return_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        "must not point primary authority or thin-router re-entry at aoa-routing" in issue.message
        for issue in issues
    )


def test_validate_generated_outputs_rejects_stale_return_navigation_surface(
    tmp_path: Path,
) -> None:
    generated_dir, roots = build_fixture_generated(tmp_path)
    return_path = generated_dir / "return_navigation_hints.min.json"
    payload = json.loads(return_path.read_text(encoding="utf-8"))
    payload["federation_kind_returns"][0]["ownership_note"] = "stale routing snapshot"
    write_json(return_path, payload)

    issues = validate_fixture_generated(generated_dir, roots)
    assert any(
        issue.location == "return_navigation_hints.min.json"
        and "canonical rebuild from current sibling catalogs" in issue.message
        for issue in issues
    )
