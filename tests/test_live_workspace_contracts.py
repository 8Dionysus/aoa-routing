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

    def test_live_workspace_playbook_routes_resolve_to_registry_activation_and_federation_surfaces(self) -> None:
        federation = load_json(REPO_ROOT / "generated" / "federation_entrypoints.min.json")
        registry = load_json(LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_registry.min.json")
        activation = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_activation_surfaces.min.json"
        )
        federation_surfaces = load_json(
            LIVE_ROOTS["aoa-playbooks"] / "generated" / "playbook_federation_surfaces.min.json"
        )

        routed_playbook_ids = [
            entry["id"]
            for entry in federation["entrypoints"]
            if entry["kind"] == "playbook"
        ]
        registry_ids = [item["id"] for item in registry["playbooks"]]
        activation_ids = [item["playbook_id"] for item in activation]
        federation_ids = [item["playbook_id"] for item in federation_surfaces]

        self.assertEqual(routed_playbook_ids, registry_ids)
        self.assertTrue(set(activation_ids).issubset(set(routed_playbook_ids)))
        self.assertTrue(set(federation_ids).issubset(set(routed_playbook_ids)))
        self.assertIsInstance(activation, list)
        self.assertIsInstance(federation_surfaces, list)

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

        kag_action = tos_kag_view["next_actions"][2]
        kag_payload = load_json(LIVE_ROOTS["aoa-kag"] / kag_action["target_surface"])
        retrieval_ids = [route["retrieval_id"] for route in kag_payload["routes"]]
        self.assertIn(kag_action["target_value"], retrieval_ids)
        self.assertEqual(kag_payload["surface_id"], "AOA-K-0011")


if __name__ == "__main__":
    unittest.main()
