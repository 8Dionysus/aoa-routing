import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import router_core


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestTosTinyEntryHopCompatibility(unittest.TestCase):
    def make_payload(self, **overrides: str) -> dict[str, str]:
        payload = {
            "route_id": "tos-tiny-entry.zarathustra-prologue",
            "root_surface": "README.md",
            "node_kind": "source_node",
            "node_id": "tos.source.thus-spoke-zarathustra.prologue",
            "capsule_surface": "docs/ZARATHUSTRA_TRILINGUAL_ENTRY.md",
            "authority_surface": "examples/source_node.example.json",
            "fallback": "docs/KNOWLEDGE_MODEL.md",
            "non_identity_boundary": (
                "This tiny-entry route is an orientation aid inside Tree of Sophia. "
                "It does not replace ToS-authored authority and does not delegate "
                "authority to aoa-kag, aoa-routing, or any other downstream derived system."
            ),
        }
        payload.update(overrides)
        return payload

    def write_tos_root(self, tos_root: Path, payload: dict[str, str]) -> None:
        write_text(tos_root / "README.md", "# Tree-of-Sophia\n")
        write_text(tos_root / "docs" / "ZARATHUSTRA_TRILINGUAL_ENTRY.md", "# Capsule\n")
        write_text(tos_root / "docs" / "KNOWLEDGE_MODEL.md", "# Knowledge Model\n")
        write_text(tos_root / "docs" / "OTHER.md", "# Other\n")
        write_text(tos_root / "examples" / "source_node.example.json", "{}\n")
        write_text(tos_root / "examples" / "concept_node.example.json", "{}\n")
        write_text(
            tos_root / "examples" / "tos_tiny_entry_route.example.json",
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        )

    def test_accepts_bounded_hop_only(self) -> None:
        payload = self.make_payload(bounded_hop="examples/concept_node.example.json")
        with tempfile.TemporaryDirectory() as tmpdir:
            tos_root = Path(tmpdir)
            self.write_tos_root(tos_root, payload)
            route_path, loaded = router_core.load_tos_tiny_entry_route(tos_root)

        self.assertEqual(route_path, "examples/tos_tiny_entry_route.example.json")
        self.assertEqual(loaded["bounded_hop"], "examples/concept_node.example.json")

    def test_accepts_matching_primary_and_legacy_hops(self) -> None:
        payload = self.make_payload(
            bounded_hop="examples/concept_node.example.json",
            lineage_or_context_hop="examples/concept_node.example.json",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            tos_root = Path(tmpdir)
            self.write_tos_root(tos_root, payload)
            _, loaded = router_core.load_tos_tiny_entry_route(tos_root)

        self.assertEqual(loaded["bounded_hop"], loaded["lineage_or_context_hop"])

    def test_rejects_mismatched_primary_and_legacy_hops(self) -> None:
        payload = self.make_payload(
            bounded_hop="examples/concept_node.example.json",
            lineage_or_context_hop="docs/OTHER.md",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            tos_root = Path(tmpdir)
            self.write_tos_root(tos_root, payload)
            with self.assertRaises(router_core.RouterError) as exc:
                router_core.load_tos_tiny_entry_route(tos_root)

        message = str(exc.exception)
        self.assertIn("bounded_hop", message)
        self.assertIn("lineage_or_context_hop", message)


if __name__ == "__main__":
    unittest.main()
