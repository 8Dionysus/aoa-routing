from __future__ import annotations

import json
import unittest
from pathlib import Path

import build_router
import validate_router
from _wave9_router_lib import build_decision_packet, preselect


REPO_ROOT = Path(__file__).resolve().parents[1]
LIVE_ROOTS = {
    "aoa-techniques": Path("/srv/aoa-techniques"),
    "aoa-skills": Path("/srv/aoa-skills"),
    "aoa-evals": Path("/srv/aoa-evals"),
    "aoa-memo": Path("/srv/aoa-memo"),
    "aoa-stats": Path("/srv/aoa-stats"),
    "aoa-sdk": Path("/srv/aoa-sdk"),
    "aoa-agents": Path("/srv/aoa-agents"),
    "Agents-of-Abyss": Path("/srv/Agents-of-Abyss"),
    "aoa-playbooks": Path("/srv/aoa-playbooks"),
    "aoa-kag": Path("/srv/aoa-kag"),
    "Tree-of-Sophia": Path("/srv/Tree-of-Sophia"),
    "Dionysus": Path("/srv/Dionysus"),
    "8Dionysus": Path("/srv/8Dionysus"),
    "abyss-stack": Path("/home/dionysus/src/abyss-stack"),
}
MISSING_LIVE_ROOTS = sorted(
    repo_name for repo_name, repo_root in LIVE_ROOTS.items() if not repo_root.exists()
)
LIVE_REQUIRED_INPUTS = {
    "Agents-of-Abyss": [Path("generated/center_entry_map.min.json")],
    "aoa-skills": [
        Path("generated/tiny_router_candidate_bands.json"),
        Path("generated/tiny_router_skill_signals.json"),
        Path("generated/skill_capsules.json"),
        Path("generated/local_adapter_manifest.json"),
        Path("generated/context_retention_manifest.json"),
    ],
    "aoa-stats": [Path("generated/stress_recovery_window_summary.min.json")],
    "Tree-of-Sophia": [Path("generated/root_entry_map.min.json")],
    "8Dionysus": [Path("generated/public_route_map.min.json")],
}
MISSING_LIVE_INPUTS = sorted(
    f"{repo_name}/{relative_path.as_posix()}"
    for repo_name, relative_paths in LIVE_REQUIRED_INPUTS.items()
    for relative_path in relative_paths
    if not (LIVE_ROOTS[repo_name] / relative_path).exists()
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@unittest.skipUnless(
    not MISSING_LIVE_ROOTS and not MISSING_LIVE_INPUTS,
    "live /srv workspace roots or required generated inputs missing: "
    + ", ".join(MISSING_LIVE_ROOTS + MISSING_LIVE_INPUTS),
)
class LiveWorkspaceContractTests(unittest.TestCase):
    def test_live_workspace_rebuild_matches_checked_in_generated_outputs(self) -> None:
        outputs = build_router.build_outputs(
            LIVE_ROOTS["aoa-techniques"],
            LIVE_ROOTS["aoa-skills"],
            LIVE_ROOTS["aoa-evals"],
            LIVE_ROOTS["aoa-memo"],
            LIVE_ROOTS["aoa-stats"],
            LIVE_ROOTS["aoa-agents"],
            LIVE_ROOTS["Agents-of-Abyss"],
            LIVE_ROOTS["aoa-playbooks"],
            LIVE_ROOTS["aoa-kag"],
            LIVE_ROOTS["Tree-of-Sophia"],
            LIVE_ROOTS["aoa-sdk"],
            LIVE_ROOTS["Dionysus"],
            LIVE_ROOTS["8Dionysus"],
            LIVE_ROOTS["abyss-stack"],
        )

        mismatches = build_router.validate_generated_dir_matches_outputs(
            outputs,
            generated_dir=REPO_ROOT / "generated",
        )

        self.assertEqual(mismatches, [])

    def test_live_workspace_generated_outputs_validate_cleanly(self) -> None:
        issues = validate_router.validate_generated_outputs(
            REPO_ROOT / "generated",
            LIVE_ROOTS["aoa-techniques"],
            LIVE_ROOTS["aoa-skills"],
            LIVE_ROOTS["aoa-evals"],
            LIVE_ROOTS["aoa-memo"],
            LIVE_ROOTS["aoa-stats"],
            LIVE_ROOTS["aoa-agents"],
            LIVE_ROOTS["Agents-of-Abyss"],
            LIVE_ROOTS["aoa-playbooks"],
            LIVE_ROOTS["aoa-kag"],
            LIVE_ROOTS["Tree-of-Sophia"],
            LIVE_ROOTS["aoa-sdk"],
            LIVE_ROOTS["Dionysus"],
            LIVE_ROOTS["8Dionysus"],
            LIVE_ROOTS["abyss-stack"],
        )

        self.assertEqual(issues, [])

    def test_live_workspace_runtime_seed_and_profile_capsules_stay_language_neutral(self) -> None:
        federation = load_json(REPO_ROOT / "generated" / "federation_entrypoints.min.json")
        entry_by_id = {
            entry["id"]: entry
            for entry in federation["entrypoints"]
            if entry["id"] in {
                "aoa-sdk-control-plane",
                "dionysus-seed-garden",
                "aoa-stats-summary-catalog",
                "abyss-stack-diagnostic-spine",
                "8dionysus-public-route-map",
            }
        }

        sdk_payload = load_json(LIVE_ROOTS["aoa-sdk"] / "generated" / "workspace_control_plane.min.json")
        self.assertEqual(
            entry_by_id["aoa-sdk-control-plane"]["capsule_surface"],
            "aoa-sdk:generated/workspace_control_plane.min.json",
        )
        self.assertEqual(sdk_payload["schema_version"], "aoa_sdk_workspace_control_plane_v2")
        self.assertEqual(sdk_payload["schema_ref"], "schemas/workspace-control-plane.schema.json")
        self.assertTrue(
            all(
                not ref.startswith(("src/", "scripts/"))
                for route in sdk_payload["routes"]
                for ref in [route["surface_ref"], *route["verification_refs"]]
            )
        )

        seed_payload = load_json(LIVE_ROOTS["Dionysus"] / "generated" / "seed_route_map.min.json")
        self.assertEqual(
            entry_by_id["dionysus-seed-garden"]["capsule_surface"],
            "Dionysus:generated/seed_route_map.min.json",
        )
        self.assertEqual(seed_payload["schema_version"], "dionysus_seed_route_map_v2")
        self.assertEqual(seed_payload["schema_ref"], "schemas/seed-route-map.schema.json")
        self.assertTrue(
            all(
                not ref.partition("#")[0].startswith(("src/", "scripts/"))
                for route in seed_payload["routes"]
                for ref in [route["surface_ref"], *route["verification_refs"]]
            )
        )

        stats_payload = load_json(LIVE_ROOTS["aoa-stats"] / "generated" / "summary_surface_catalog.min.json")
        self.assertEqual(
            entry_by_id["aoa-stats-summary-catalog"]["capsule_surface"],
            "aoa-stats:generated/summary_surface_catalog.min.json",
        )
        self.assertEqual(stats_payload["schema_version"], "aoa_stats_summary_surface_catalog_v2")
        self.assertEqual(stats_payload["schema_ref"], "schemas/summary-surface-catalog.schema.json")
        self.assertEqual(stats_payload["owner_repo"], "aoa-stats")
        self.assertEqual(stats_payload["surface_kind"], "runtime_surface")
        self.assertEqual(stats_payload["authority_ref"], "docs/ARCHITECTURE.md")
        self.assertEqual(
            stats_payload["validation_refs"],
            [
                "scripts/build_views.py",
                "scripts/validate_repo.py",
                "tests/test_summary_surface_catalog.py",
            ],
        )
        self.assertTrue(all("schema_ref" in entry and "surface_ref" in entry for entry in stats_payload["surfaces"]))
        self.assertTrue(all("path" not in entry for entry in stats_payload["surfaces"]))

        abyss_payload = load_json(LIVE_ROOTS["abyss-stack"] / "generated" / "diagnostic_surface_catalog.min.json")
        self.assertEqual(
            entry_by_id["abyss-stack-diagnostic-spine"]["capsule_surface"],
            "abyss-stack:generated/diagnostic_surface_catalog.min.json",
        )
        self.assertTrue(all("schema_ref" in entry and "example_ref" in entry for entry in abyss_payload["surfaces"]))

        profile_payload = load_json(LIVE_ROOTS["8Dionysus"] / "generated" / "public_route_map.min.json")
        self.assertEqual(
            entry_by_id["8dionysus-public-route-map"]["capsule_surface"],
            "8Dionysus:generated/public_route_map.min.json",
        )
        self.assertEqual(profile_payload["schema_version"], "8dionysus_public_route_map_v2")
        self.assertEqual(profile_payload["schema_ref"], "schemas/public-route-map.schema.json")
        self.assertTrue(
            all(
                ":src/" not in ref and ":scripts/" not in ref
                for route in profile_payload["routes"]
                for ref in [route["capsule_ref"], route["authority_ref"], *route["verification_refs"]]
            )
        )

    def test_live_workspace_root_capsules_are_owner_owned_zero_entry_surfaces(self) -> None:
        federation = load_json(REPO_ROOT / "generated" / "federation_entrypoints.min.json")
        root_by_id = {entry["id"]: entry for entry in federation["root_entries"]}

        aoa_payload = load_json(LIVE_ROOTS["Agents-of-Abyss"] / "generated" / "center_entry_map.min.json")
        self.assertEqual(
            root_by_id["aoa-root"]["capsule_surface"],
            "Agents-of-Abyss:generated/center_entry_map.min.json",
        )
        self.assertEqual(aoa_payload["schema_version"], "aoa_center_entry_map_v1")
        self.assertEqual(aoa_payload["schema_ref"], "schemas/center-entry-map.schema.json")
        self.assertEqual(aoa_payload["owner_repo"], "Agents-of-Abyss")
        self.assertEqual(aoa_payload["surface_kind"], "center_entry_map")
        self.assertEqual(aoa_payload["authority_ref"], "CHARTER.md")
        self.assertEqual(aoa_payload["public_root_ref"], "README.md")
        self.assertEqual(
            [route["route_id"] for route in aoa_payload["routes"]],
            ["center-overview", "constitutional-boundary", "public-contour", "source-of-truth-rules"],
        )
        self.assertEqual(
            root_by_id["aoa-root"]["next_actions"],
            [
                {
                    "verb": "inspect",
                    "target_repo": "Agents-of-Abyss",
                    "target_surface": "generated/center_entry_map.min.json",
                    "match_key": "route_id",
                    "target_value": "center-overview",
                },
                {
                    "verb": "inspect",
                    "target_repo": "Agents-of-Abyss",
                    "target_surface": "generated/center_entry_map.min.json",
                    "match_key": "route_id",
                    "target_value": "public-contour",
                },
                {
                    "verb": "inspect",
                    "target_repo": "Agents-of-Abyss",
                    "target_surface": "generated/center_entry_map.min.json",
                    "match_key": "route_id",
                    "target_value": "source-of-truth-rules",
                },
            ],
        )

        tos_payload = load_json(LIVE_ROOTS["Tree-of-Sophia"] / "generated" / "root_entry_map.min.json")
        self.assertEqual(
            root_by_id["tos-root"]["capsule_surface"],
            "Tree-of-Sophia:generated/root_entry_map.min.json",
        )
        self.assertEqual(tos_payload["schema_version"], "tos_root_entry_map_v1")
        self.assertEqual(tos_payload["schema_ref"], "schemas/root-entry-map.schema.json")
        self.assertEqual(tos_payload["owner_repo"], "Tree-of-Sophia")
        self.assertEqual(tos_payload["surface_kind"], "root_entry_map")
        self.assertEqual(tos_payload["authority_ref"], "CHARTER.md")
        self.assertEqual(tos_payload["public_root_ref"], "README.md")
        self.assertEqual(
            [route["route_id"] for route in tos_payload["routes"]],
            ["current-tiny-entry", "tree-first-model", "bounded-export"],
        )
        self.assertEqual(
            root_by_id["tos-root"]["next_actions"],
            [
                {
                    "verb": "inspect",
                    "target_repo": "Tree-of-Sophia",
                    "target_surface": "generated/root_entry_map.min.json",
                    "match_key": "route_id",
                    "target_value": "current-tiny-entry",
                },
                {
                    "verb": "inspect",
                    "target_repo": "Tree-of-Sophia",
                    "target_surface": "generated/root_entry_map.min.json",
                    "match_key": "route_id",
                    "target_value": "tree-first-model",
                },
                {
                    "verb": "inspect",
                    "target_repo": "Tree-of-Sophia",
                    "target_surface": "generated/root_entry_map.min.json",
                    "match_key": "route_id",
                    "target_value": "bounded-export",
                },
            ],
        )

    def test_live_workspace_tiny_root_starters_reach_owner_owned_zero_entry_routes(self) -> None:
        tiny = load_json(REPO_ROOT / "generated" / "tiny_model_entrypoints.json")
        federation = load_json(REPO_ROOT / "generated" / "federation_entrypoints.min.json")
        root_by_id = {entry["id"]: entry for entry in federation["root_entries"]}
        federation_starters = {
            starter["name"]: starter for starter in tiny["federation_starters"]
        }

        aoa_root = root_by_id[federation_starters["aoa-root"]["target_value"]]
        aoa_first_action = aoa_root["next_actions"][0]
        self.assertEqual(aoa_first_action["target_repo"], "Agents-of-Abyss")
        aoa_capsule = load_json(LIVE_ROOTS["Agents-of-Abyss"] / "generated" / "center_entry_map.min.json")
        aoa_route_by_id = {route["route_id"]: route for route in aoa_capsule["routes"]}
        aoa_route = aoa_route_by_id[aoa_first_action["target_value"]]
        self.assertEqual(aoa_route["surface_ref"], "README.md")
        self.assertTrue((LIVE_ROOTS["Agents-of-Abyss"] / aoa_route["surface_ref"]).exists())
        self.assertTrue(
            all((LIVE_ROOTS["Agents-of-Abyss"] / ref).exists() for ref in aoa_route["verification_refs"])
        )

        tos_root = root_by_id[federation_starters["tos-root"]["target_value"]]
        tos_first_action = tos_root["next_actions"][0]
        self.assertEqual(tos_first_action["target_repo"], "Tree-of-Sophia")
        tos_capsule = load_json(LIVE_ROOTS["Tree-of-Sophia"] / "generated" / "root_entry_map.min.json")
        tos_route_by_id = {route["route_id"]: route for route in tos_capsule["routes"]}
        tos_route = tos_route_by_id[tos_first_action["target_value"]]
        self.assertEqual(tos_route["surface_ref"], "examples/tos_tiny_entry_route.example.json")
        self.assertTrue((LIVE_ROOTS["Tree-of-Sophia"] / tos_route["surface_ref"]).exists())
        self.assertTrue(
            all((LIVE_ROOTS["Tree-of-Sophia"] / ref).exists() for ref in tos_route["verification_refs"])
        )

    def test_live_workspace_skill_root_handoff_reaches_source_owned_activation_seams(self) -> None:
        tiny = load_json(REPO_ROOT / "generated" / "tiny_model_entrypoints.json")
        two_stage = load_json(REPO_ROOT / "generated" / "two_stage_skill_entrypoints.json")
        policy = load_json(REPO_ROOT / "config" / "two_stage_router_policy.json")
        eval_cases = {
            entry["case_id"]: entry
            for entry in load_jsonl(REPO_ROOT / "generated" / "two_stage_router_eval_cases.jsonl")
        }
        skill_root = next(starter for starter in tiny["starters"] if starter["name"] == "skill-root")
        self.assertEqual(skill_root["adjacent_handoff"]["target_surface"], "generated/two_stage_skill_entrypoints.json")
        self.assertEqual(two_stage["tiny_model_handoff"]["starter_ref"], "skill-root")

        skills_root = LIVE_ROOTS["aoa-skills"]
        signals_doc = load_json(skills_root / two_stage["stage_1"]["signals_surface"])
        bands_doc = load_json(skills_root / two_stage["stage_1"]["bands_surface"])
        capsules = {
            entry["name"]: entry
            for entry in load_json(skills_root / two_stage["stage_2"]["shortlist_surface"])["skills"]
        }
        adapters = {
            entry["name"]: entry
            for entry in load_json(skills_root / two_stage["stage_2"]["activation_manifest"])["skills"]
        }
        contexts = {
            entry["name"]: entry
            for entry in load_json(skills_root / two_stage["stage_2"]["context_manifest"])["skills"]
        }

        for case_id, expected_mode in [
            ("tiny-positive-aoa-adr-write", "activate-candidate"),
            ("tiny-positive-abyss-safe-infra-change", "manual-invocation-required"),
        ]:
            with self.subTest(case_id=case_id):
                case = eval_cases[case_id]
                preselected = preselect(
                    task=case["prompt"],
                    signals_doc=signals_doc,
                    bands_doc=bands_doc,
                    policy=policy,
                    top_k=two_stage["stage_1"]["top_k_default"],
                    repo_family=case.get("repo_family_hint"),
                )
                packet = build_decision_packet(
                    case["prompt"],
                    preselected,
                    skills_root,
                    max_shortlist=two_stage["stage_2"]["max_shortlist"],
                )
                self.assertEqual(packet["suggested_decision"]["decision_mode"], expected_mode)
                self.assertEqual(packet["suggested_decision"]["skill"], case["expected_top1"])
                candidate = packet["candidates"][0]
                self.assertEqual(candidate["name"], case["expected_top1"])
                self.assertIn(candidate["name"], capsules)
                self.assertIn(candidate["name"], adapters)
                self.assertIn(candidate["name"], contexts)
                self.assertTrue((skills_root / capsules[candidate["name"]]["skill_path"]).exists())
                self.assertEqual(
                    adapters[candidate["name"]]["invocation_mode"],
                    candidate["invocation_mode"],
                )
                self.assertEqual(
                    candidate["manual_invocation_required"],
                    expected_mode == "manual-invocation-required",
                )
                self.assertTrue(contexts[candidate["name"]]["rehydration_hint"])

    def test_live_workspace_routing_federation_envelopes_are_normalized_v2(self) -> None:
        federation = load_json(REPO_ROOT / "generated" / "federation_entrypoints.min.json")
        tiny = load_json(REPO_ROOT / "generated" / "tiny_model_entrypoints.json")
        shortlist = load_json(REPO_ROOT / "generated" / "owner_layer_shortlist.min.json")
        returns = load_json(REPO_ROOT / "generated" / "return_navigation_hints.min.json")
        two_stage_entrypoints = load_json(REPO_ROOT / "generated" / "two_stage_skill_entrypoints.json")
        two_stage_prompt_blocks = load_json(REPO_ROOT / "generated" / "two_stage_router_prompt_blocks.json")
        two_stage_tool_schemas = load_json(REPO_ROOT / "generated" / "two_stage_router_tool_schemas.json")
        two_stage_examples = load_json(REPO_ROOT / "generated" / "two_stage_router_examples.json")
        two_stage_manifest = load_json(REPO_ROOT / "generated" / "two_stage_router_manifest.json")

        self.assertEqual(federation["schema_version"], "aoa_routing_federation_entrypoints_v2")
        self.assertEqual(federation["schema_ref"], "schemas/federation-entrypoints.schema.json")
        self.assertEqual(federation["owner_repo"], "aoa-routing")
        self.assertEqual(federation["surface_kind"], "federation_entrypoints")
        self.assertEqual(tiny["schema_version"], "aoa_routing_tiny_model_entrypoints_v2")
        self.assertEqual(tiny["schema_ref"], "schemas/tiny-model-entrypoints.schema.json")
        self.assertEqual(tiny["owner_repo"], "aoa-routing")
        self.assertEqual(tiny["surface_kind"], "tiny_model_entrypoints")
        self.assertEqual(shortlist["schema_version"], "aoa_routing_owner_layer_shortlist_v2")
        self.assertEqual(shortlist["schema_ref"], "schemas/owner-layer-shortlist.schema.json")
        self.assertEqual(shortlist["owner_repo"], "aoa-routing")
        self.assertEqual(shortlist["surface_kind"], "owner_layer_shortlist")
        self.assertEqual(returns["schema_version"], "aoa_routing_return_navigation_hints_v2")
        self.assertEqual(returns["schema_ref"], "schemas/return-navigation-hints.schema.json")
        self.assertEqual(returns["owner_repo"], "aoa-routing")
        self.assertEqual(returns["surface_kind"], "return_navigation_hints")
        self.assertEqual(two_stage_entrypoints["schema_version"], "aoa_routing_two_stage_skill_entrypoints_v2")
        self.assertEqual(two_stage_entrypoints["schema_ref"], "schemas/two-stage-skill-entrypoints.schema.json")
        self.assertEqual(two_stage_entrypoints["owner_repo"], "aoa-routing")
        self.assertEqual(two_stage_entrypoints["surface_kind"], "two_stage_skill_entrypoints")
        self.assertEqual(two_stage_prompt_blocks["schema_version"], "aoa_routing_two_stage_router_prompt_blocks_v2")
        self.assertEqual(two_stage_prompt_blocks["schema_ref"], "schemas/two-stage-router-prompt-blocks.schema.json")
        self.assertEqual(two_stage_prompt_blocks["owner_repo"], "aoa-routing")
        self.assertEqual(two_stage_prompt_blocks["surface_kind"], "two_stage_router_prompt_blocks")
        self.assertEqual(two_stage_prompt_blocks["low_context_boundary"]["wording_scope"], "routing-owned")
        self.assertEqual(two_stage_prompt_blocks["low_context_boundary"]["source_payload_copying"], "forbidden")
        self.assertEqual(two_stage_tool_schemas["schema_version"], "aoa_routing_two_stage_router_tool_schemas_v2")
        self.assertEqual(two_stage_tool_schemas["schema_ref"], "schemas/two-stage-router-tool-schemas.schema.json")
        self.assertEqual(two_stage_tool_schemas["owner_repo"], "aoa-routing")
        self.assertEqual(two_stage_tool_schemas["surface_kind"], "two_stage_router_tool_schemas")
        self.assertEqual(two_stage_tool_schemas["low_context_boundary"], two_stage_prompt_blocks["low_context_boundary"])
        self.assertEqual(two_stage_examples["schema_version"], "aoa_routing_two_stage_router_examples_v2")
        self.assertEqual(two_stage_examples["schema_ref"], "schemas/two-stage-router-examples.schema.json")
        self.assertEqual(two_stage_examples["owner_repo"], "aoa-routing")
        self.assertEqual(two_stage_examples["surface_kind"], "two_stage_router_examples")
        self.assertEqual(two_stage_manifest["schema_version"], "aoa_routing_two_stage_router_manifest_v2")
        self.assertEqual(two_stage_manifest["schema_ref"], "schemas/two-stage-router-manifest.schema.json")
        self.assertEqual(two_stage_manifest["owner_repo"], "aoa-routing")
        self.assertEqual(two_stage_manifest["surface_kind"], "two_stage_router_manifest")

    def test_live_workspace_playbook_routes_resolve_to_registry_activation_federation_review_status_packet_contracts_and_intake(self) -> None:
        federation = load_json(REPO_ROOT / "generated" / "federation_entrypoints.min.json")
        registry = load_json(LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_registry.min.json")
        activation = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_activation_surfaces.min.json"
        )
        federation_surfaces = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_federation_surfaces.min.json"
        )
        review_status = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_review_status.min.json"
        )
        review_packet_contracts = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_review_packet_contracts.min.json"
        )
        review_intake = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_review_intake.min.json"
        )

        routed_playbook_ids = [
            entry["id"]
            for entry in federation["entrypoints"]
            if entry["kind"] == "playbook"
        ]
        registry_ids = [item["id"] for item in registry["playbooks"]]
        activation_ids = [item["playbook_id"] for item in activation]
        federation_ids = [item["playbook_id"] for item in federation_surfaces]
        review_ids = [item["playbook_id"] for item in review_status["playbooks"]]
        review_packet_ids = [item["playbook_id"] for item in review_packet_contracts["playbooks"]]
        review_intake_ids = [item["playbook_id"] for item in review_intake["playbooks"]]
        gated_review_packet_ids = [
            item["playbook_id"]
            for item in review_packet_contracts["playbooks"]
            if item.get("gate_verdict")
        ]
        gated_review_intake_ids = [
            item["playbook_id"]
            for item in review_intake["playbooks"]
            if item.get("gate_verdict")
        ]

        self.assertEqual(routed_playbook_ids, registry_ids)
        self.assertTrue(set(activation_ids).issubset(set(routed_playbook_ids)))
        self.assertTrue(set(federation_ids).issubset(set(routed_playbook_ids)))
        self.assertTrue(set(review_ids).issubset(set(routed_playbook_ids)))
        self.assertTrue(set(review_packet_ids).issubset(set(routed_playbook_ids)))
        self.assertTrue(set(review_intake_ids).issubset(set(routed_playbook_ids)))
        self.assertEqual(review_ids, gated_review_packet_ids)
        self.assertEqual(review_ids, gated_review_intake_ids)
        self.assertIsInstance(activation, list)
        self.assertIsInstance(federation_surfaces, list)
        self.assertEqual(review_status["schema_version"], 1)
        self.assertEqual(review_packet_contracts["schema_version"], 1)
        self.assertEqual(review_intake["schema_version"], 1)

        review_by_id = {item["playbook_id"]: item for item in review_status["playbooks"]}
        self.assertEqual(review_by_id["AOA-P-0017"]["gate_verdict"], "composition-landed")
        self.assertEqual(review_by_id["AOA-P-0018"]["gate_verdict"], "hold")
        self.assertEqual(review_by_id["AOA-P-0019"]["gate_verdict"], "hold")
        self.assertEqual(review_by_id["AOA-P-0020"]["gate_verdict"], "hold")
        self.assertEqual(review_by_id["AOA-P-0021"]["gate_verdict"], "composition-landed")
        self.assertEqual(review_by_id["AOA-P-0024"]["gate_verdict"], "hold")

        packet_by_id = {item["playbook_id"]: item for item in review_packet_contracts["playbooks"]}
        self.assertEqual(packet_by_id["AOA-P-0011"]["memo_runtime_surfaces"], ["approval_record"])
        self.assertEqual(packet_by_id["AOA-P-0017"]["gate_verdict"], "composition-landed")
        self.assertEqual(
            packet_by_id["AOA-P-0017"]["source_review_refs"][0],
            "playbooks/split-wave-cross-repo-rollout/PLAYBOOK.md",
        )
        self.assertEqual(
            packet_by_id["AOA-P-0017"]["source_review_refs"][1],
            "docs/gate-reviews/split-wave-cross-repo-rollout.md",
        )
        self.assertEqual(packet_by_id["AOA-P-0021"]["gate_verdict"], "composition-landed")
        self.assertEqual(
            packet_by_id["AOA-P-0021"]["source_review_refs"][:2],
            [
                "playbooks/owner-first-capability-landing/PLAYBOOK.md",
                "docs/gate-reviews/owner-first-capability-landing.md",
            ],
        )
        self.assertIn(
            "docs/real-runs/2026-04-07.owner-first-capability-landing.md",
            packet_by_id["AOA-P-0021"]["source_review_refs"],
        )
        self.assertEqual(packet_by_id["AOA-P-0024"]["gate_verdict"], "hold")
        self.assertEqual(
            packet_by_id["AOA-P-0024"]["source_review_refs"],
            [
                "playbooks/federated-live-publisher-activation/PLAYBOOK.md",
                "docs/gate-reviews/federated-live-publisher-activation.md",
                "docs/real-runs/2026-04-07.federated-live-publisher-activation.md",
            ],
        )

        intake_by_id = {item["playbook_id"]: item for item in review_intake["playbooks"]}
        self.assertEqual(intake_by_id["AOA-P-0017"]["gate_verdict"], "composition-landed")
        self.assertEqual(intake_by_id["AOA-P-0017"]["composition_posture"], "landed")
        self.assertEqual(intake_by_id["AOA-P-0019"]["gate_verdict"], "hold")
        self.assertEqual(intake_by_id["AOA-P-0019"]["composition_posture"], "awaiting-reviewed-run")
        self.assertEqual(intake_by_id["AOA-P-0021"]["gate_verdict"], "composition-landed")
        self.assertEqual(intake_by_id["AOA-P-0021"]["composition_posture"], "landed")
        self.assertEqual(intake_by_id["AOA-P-0024"]["gate_verdict"], "hold")
        self.assertEqual(intake_by_id["AOA-P-0024"]["composition_posture"], "held-after-review")
        self.assertEqual(
            intake_by_id["AOA-P-0017"]["accepted_packet_kinds"],
            packet_by_id["AOA-P-0017"]["candidate_packet_kinds"],
        )
        self.assertEqual(
            intake_by_id["AOA-P-0017"]["review_outcome_targets"]["gate_reviews"],
            ["docs/gate-reviews/split-wave-cross-repo-rollout.md"],
        )

    def test_live_workspace_playbook_eval_and_memo_intake_chain_resolves_to_real_surfaces(self) -> None:
        review_packet_contracts = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_review_packet_contracts.min.json"
        )
        review_intake = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_review_intake.min.json"
        )
        runtime_template_index = load_json(
            LIVE_ROOTS["aoa-evals"] / "generated" / "runtime_candidate_template_index.min.json"
        )
        runtime_candidate_intake = load_json(
            LIVE_ROOTS["aoa-evals"] / "generated" / "runtime_candidate_intake.min.json"
        )
        runtime_writeback_targets = load_json(
            LIVE_ROOTS["aoa-memo"] / "generated" / "runtime_writeback_targets.min.json"
        )
        runtime_writeback_intake = load_json(
            LIVE_ROOTS["aoa-memo"] / "generated" / "runtime_writeback_intake.min.json"
        )

        available_eval_anchors = {
            entry["eval_anchor"]
            for entry in runtime_template_index["templates"]
            if entry.get("eval_anchor")
        }
        normalized_eval_template_artifacts = {
            (entry["template_kind"], entry["template_name"]): entry["required_runtime_artifacts"]
            for entry in runtime_template_index["templates"]
        }
        available_runtime_surfaces = {
            entry["runtime_surface"] for entry in runtime_writeback_targets["targets"]
        }
        intake_by_id = {item["playbook_id"]: item for item in review_intake["playbooks"]}
        template_intake_by_key = {
            (entry["template_kind"], entry["template_name"]): entry
            for entry in runtime_candidate_intake["templates"]
        }
        memo_intake_by_surface = {
            entry["runtime_surface"]: entry for entry in runtime_writeback_intake["targets"]
        }

        for contract in review_packet_contracts["playbooks"]:
            self.assertTrue(set(contract["eval_anchors"]).issubset(available_eval_anchors))
            self.assertTrue(set(contract["memo_runtime_surfaces"]).issubset(available_runtime_surfaces))
            if contract["review_required"]:
                self.assertTrue(contract["source_review_refs"])
                self.assertTrue(contract["source_review_refs"][0].endswith("/PLAYBOOK.md"))
            self.assertEqual(
                contract["candidate_packet_kinds"],
                list(dict.fromkeys(contract["candidate_packet_kinds"])),
            )
            self.assertIn(contract["playbook_id"], intake_by_id)
            intake_entry = intake_by_id[contract["playbook_id"]]
            self.assertEqual(
                intake_entry["accepted_packet_kinds"],
                contract["candidate_packet_kinds"],
            )
            self.assertTrue(intake_entry["source_review_refs"])

        by_id = {item["playbook_id"]: item for item in review_packet_contracts["playbooks"]}
        self.assertEqual(by_id["AOA-P-0011"]["eval_anchors"], ["aoa-approval-boundary-adherence"])
        self.assertEqual(by_id["AOA-P-0011"]["memo_runtime_surfaces"], ["approval_record"])
        self.assertEqual(
            by_id["AOA-P-0011"]["source_review_refs"][0],
            "playbooks/bounded-change-safe/PLAYBOOK.md",
        )
        self.assertEqual(
            by_id["AOA-P-0017"]["eval_anchors"],
            [
                "aoa-approval-boundary-adherence",
                "aoa-scope-drift-detection",
                "aoa-verification-honesty",
            ],
        )

        for template_key, required_runtime_artifacts in normalized_eval_template_artifacts.items():
            self.assertEqual(required_runtime_artifacts, list(dict.fromkeys(required_runtime_artifacts)))
            self.assertTrue(
                all(
                    artifact
                    and artifact == artifact.lower()
                    and " " not in artifact
                    for artifact in required_runtime_artifacts
                ),
                msg=f"{template_key[1]} must keep normalized required_runtime_artifacts",
            )
            intake_entry = template_intake_by_key[template_key]
            self.assertEqual(intake_entry["required_runtime_artifacts"], required_runtime_artifacts)
            self.assertTrue(intake_entry["owner_review_refs"])
            self.assertEqual(
                intake_entry["candidate_acceptance_posture"],
                "candidate_until_eval_review",
            )

        reviewed_candidate_targets = [
            entry
            for entry in runtime_writeback_targets["targets"]
            if entry["writeback_class"] == "reviewed_candidate"
        ]
        self.assertTrue(reviewed_candidate_targets)
        self.assertTrue(all(entry["requires_human_review"] for entry in reviewed_candidate_targets))
        self.assertTrue(
            all(entry["review_state_default"] == "proposed" for entry in reviewed_candidate_targets)
        )
        self.assertTrue(set(memo_intake_by_surface).issubset(available_runtime_surfaces))
        for runtime_surface, intake_entry in memo_intake_by_surface.items():
            source_entry = next(
                entry
                for entry in runtime_writeback_targets["targets"]
                if entry["runtime_surface"] == runtime_surface
            )
            self.assertEqual(intake_entry["target_kind"], source_entry["target_kind"])
            self.assertEqual(intake_entry["writeback_class"], source_entry["writeback_class"])
            self.assertEqual(intake_entry["requires_human_review"], source_entry["requires_human_review"])
            self.assertTrue(intake_entry["owner_review_refs"])
        self.assertTrue(
            all(
                memo_intake_by_surface[entry["runtime_surface"]]["intake_posture"] == "review_candidate_only"
                for entry in reviewed_candidate_targets
            )
        )

    def test_live_workspace_technique_memo_and_kag_execution_seams_resolve_to_real_surfaces(self) -> None:
        hints = load_json(REPO_ROOT / "generated" / "task_to_surface_hints.json")
        federation = load_json(REPO_ROOT / "generated" / "federation_entrypoints.min.json")
        technique_hint = next(item for item in hints["hints"] if item["kind"] == "technique")
        memo_hint = next(item for item in hints["hints"] if item["kind"] == "memo")
        tos_kag_view = next(
            entry
            for entry in federation["entrypoints"]
            if entry["kind"] == "kag_view" and entry["id"] == "Tree-of-Sophia"
        )

        techniques_root = LIVE_ROOTS["aoa-techniques"]
        technique_second_cut = technique_hint["actions"]["second_cut"]
        self.assertEqual(technique_second_cut["surface_repo"], "aoa-techniques")
        self.assertEqual(technique_second_cut["selection_axis"], "kind")
        self.assertEqual(technique_second_cut["prerequisite_axes"], ["domain"])
        kind_manifest = load_json(techniques_root / technique_second_cut["surface_file"])
        routed_kind_values = [entry["kind"] for entry in kind_manifest["kinds"]]
        self.assertEqual(kind_manifest["selection_order"], routed_kind_values)
        self.assertTrue(all(entry["technique_ids"] for entry in kind_manifest["kinds"]))

        memo_root = LIVE_ROOTS["aoa-memo"]
        memo_actions = memo_hint["actions"]
        self.assertTrue((memo_root / memo_actions["inspect"]["surface_file"]).exists())
        self.assertTrue((memo_root / memo_actions["expand"]["surface_file"]).exists())

        recall = memo_actions["recall"]
        for contract_path in recall["contracts_by_mode"].values():
            self.assertTrue((memo_root / contract_path).exists())
        for surface_path in recall["capsule_surfaces_by_mode"].values():
            self.assertTrue((memo_root / surface_path).exists())
        object_family = recall["parallel_families"]["memory_objects"]
        self.assertTrue((memo_root / object_family["inspect_surface"]).exists())
        self.assertTrue((memo_root / object_family["expand_surface"]).exists())
        for contract_path in object_family["contracts_by_mode"].values():
            self.assertTrue((memo_root / contract_path).exists())
        for surface_path in object_family["capsule_surfaces_by_mode"].values():
            self.assertTrue((memo_root / surface_path).exists())
        checkpoint_contract = load_json(
            memo_root / "examples" / "checkpoint_to_memory_contract.example.json"
        )
        writeback_targets = load_json(
            memo_root / "generated" / "runtime_writeback_targets.min.json"
        )
        writeback_intake = load_json(
            memo_root / "generated" / "runtime_writeback_intake.min.json"
        )
        mapped_runtime_surfaces = {
            item["runtime_surface"] for item in checkpoint_contract["mapping_rules"]
        }
        mapped_target_runtime_surfaces = {
            item["runtime_surface"] for item in writeback_targets["targets"]
        }
        mapped_intake_runtime_surfaces = {
            item["runtime_surface"] for item in writeback_intake["targets"]
        }
        self.assertIn("checkpoint_export", mapped_runtime_surfaces)
        self.assertIn("distillation_claim_candidate", mapped_runtime_surfaces)
        self.assertEqual(mapped_runtime_surfaces, mapped_target_runtime_surfaces)
        self.assertEqual(mapped_runtime_surfaces, mapped_intake_runtime_surfaces)

        kag_action = tos_kag_view["next_actions"][2]
        kag_payload = load_json(LIVE_ROOTS["aoa-kag"] / kag_action["target_surface"])
        retrieval_ids = [route["retrieval_id"] for route in kag_payload["routes"]]
        self.assertIn(kag_action["target_value"], retrieval_ids)
        self.assertEqual(kag_payload["surface_id"], "AOA-K-0011")


if __name__ == "__main__":
    unittest.main()
