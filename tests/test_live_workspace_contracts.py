from __future__ import annotations

import json
import unittest
from pathlib import Path

import build_router
import validate_router


REPO_ROOT = Path(__file__).resolve().parents[1]
LIVE_ROOTS = {
    "aoa-techniques": Path("/srv/aoa-techniques"),
    "aoa-skills": Path("/srv/aoa-skills"),
    "aoa-evals": Path("/srv/aoa-evals"),
    "aoa-memo": Path("/srv/aoa-memo"),
    "aoa-agents": Path("/srv/aoa-agents"),
    "Agents-of-Abyss": Path("/srv/Agents-of-Abyss"),
    "aoa-playbooks": Path("/srv/aoa-playbooks"),
    "aoa-kag": Path("/srv/aoa-kag"),
    "Tree-of-Sophia": Path("/srv/Tree-of-Sophia"),
}
MISSING_LIVE_ROOTS = sorted(
    repo_name for repo_name, repo_root in LIVE_ROOTS.items() if not repo_root.exists()
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@unittest.skipUnless(
    not MISSING_LIVE_ROOTS,
    f"live /srv workspace roots missing: {', '.join(MISSING_LIVE_ROOTS)}",
)
class LiveWorkspaceContractTests(unittest.TestCase):
    def test_live_workspace_rebuild_matches_checked_in_generated_outputs(self) -> None:
        outputs = build_router.build_outputs(
            LIVE_ROOTS["aoa-techniques"],
            LIVE_ROOTS["aoa-skills"],
            LIVE_ROOTS["aoa-evals"],
            LIVE_ROOTS["aoa-memo"],
            LIVE_ROOTS["aoa-agents"],
            LIVE_ROOTS["Agents-of-Abyss"],
            LIVE_ROOTS["aoa-playbooks"],
            LIVE_ROOTS["aoa-kag"],
            LIVE_ROOTS["Tree-of-Sophia"],
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
            LIVE_ROOTS["aoa-agents"],
            LIVE_ROOTS["Agents-of-Abyss"],
            LIVE_ROOTS["aoa-playbooks"],
            LIVE_ROOTS["aoa-kag"],
            LIVE_ROOTS["Tree-of-Sophia"],
        )

        self.assertEqual(issues, [])

    def test_live_workspace_playbook_routes_resolve_to_registry_activation_federation_review_status_and_packet_contracts(self) -> None:
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

        self.assertEqual(routed_playbook_ids, registry_ids)
        self.assertTrue(set(activation_ids).issubset(set(routed_playbook_ids)))
        self.assertTrue(set(federation_ids).issubset(set(routed_playbook_ids)))
        self.assertTrue(set(review_ids).issubset(set(routed_playbook_ids)))
        self.assertTrue(set(review_packet_ids).issubset(set(routed_playbook_ids)))
        self.assertEqual(review_ids, ["AOA-P-0017", "AOA-P-0019", "AOA-P-0020"])
        self.assertIsInstance(activation, list)
        self.assertIsInstance(federation_surfaces, list)
        self.assertEqual(review_status["schema_version"], 1)
        self.assertEqual(review_packet_contracts["schema_version"], 1)

        review_by_id = {item["playbook_id"]: item for item in review_status["playbooks"]}
        self.assertEqual(review_by_id["AOA-P-0017"]["gate_verdict"], "composition-landed")
        self.assertEqual(review_by_id["AOA-P-0019"]["gate_verdict"], "hold")
        self.assertEqual(review_by_id["AOA-P-0020"]["gate_verdict"], "hold")

        packet_by_id = {item["playbook_id"]: item for item in review_packet_contracts["playbooks"]}
        self.assertEqual(packet_by_id["AOA-P-0011"]["memo_runtime_surfaces"], ["approval_record"])
        self.assertEqual(packet_by_id["AOA-P-0017"]["gate_verdict"], "composition-landed")
        self.assertEqual(
            packet_by_id["AOA-P-0017"]["source_review_refs"][0],
            "docs/gate-reviews/split-wave-cross-repo-rollout.md",
        )

    def test_live_workspace_playbook_eval_and_memo_review_packet_chain_resolves_to_real_surfaces(self) -> None:
        review_packet_contracts = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_review_packet_contracts.min.json"
        )
        runtime_template_index = load_json(
            LIVE_ROOTS["aoa-evals"] / "generated" / "runtime_candidate_template_index.min.json"
        )
        runtime_writeback_targets = load_json(
            LIVE_ROOTS["aoa-memo"] / "generated" / "runtime_writeback_targets.min.json"
        )

        available_eval_anchors = {
            entry["eval_anchor"]
            for entry in runtime_template_index["templates"]
            if entry.get("eval_anchor")
        }
        available_runtime_surfaces = {
            entry["runtime_surface"] for entry in runtime_writeback_targets["targets"]
        }

        for contract in review_packet_contracts["playbooks"]:
            self.assertTrue(set(contract["eval_anchors"]).issubset(available_eval_anchors))
            self.assertTrue(set(contract["memo_runtime_surfaces"]).issubset(available_runtime_surfaces))

        by_id = {item["playbook_id"]: item for item in review_packet_contracts["playbooks"]}
        self.assertEqual(by_id["AOA-P-0011"]["eval_anchors"], ["aoa-approval-boundary-adherence"])
        self.assertEqual(by_id["AOA-P-0011"]["memo_runtime_surfaces"], ["approval_record"])
        self.assertEqual(by_id["AOA-P-0017"]["eval_anchors"], ["aoa-approval-boundary-adherence"])

    def test_live_workspace_memo_and_kag_execution_seams_resolve_to_real_surfaces(self) -> None:
        hints = load_json(REPO_ROOT / "generated" / "task_to_surface_hints.json")
        federation = load_json(REPO_ROOT / "generated" / "federation_entrypoints.min.json")
        memo_hint = next(item for item in hints["hints"] if item["kind"] == "memo")
        tos_kag_view = next(
            entry
            for entry in federation["entrypoints"]
            if entry["kind"] == "kag_view" and entry["id"] == "Tree-of-Sophia"
        )

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
        mapped_runtime_surfaces = {
            item["runtime_surface"] for item in checkpoint_contract["mapping_rules"]
        }
        mapped_target_runtime_surfaces = {
            item["runtime_surface"] for item in writeback_targets["targets"]
        }
        self.assertIn("checkpoint_export", mapped_runtime_surfaces)
        self.assertIn("distillation_claim_candidate", mapped_runtime_surfaces)
        self.assertEqual(mapped_runtime_surfaces, mapped_target_runtime_surfaces)

        kag_action = tos_kag_view["next_actions"][2]
        kag_payload = load_json(LIVE_ROOTS["aoa-kag"] / kag_action["target_surface"])
        retrieval_ids = [route["retrieval_id"] for route in kag_payload["routes"]]
        self.assertIn(kag_action["target_value"], retrieval_ids)
        self.assertEqual(kag_payload["surface_id"], "AOA-K-0011")


if __name__ == "__main__":
    unittest.main()
