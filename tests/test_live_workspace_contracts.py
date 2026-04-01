from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
