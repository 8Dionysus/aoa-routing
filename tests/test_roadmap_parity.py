from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_roadmap_federation_milestone_mentions_current_active_entry_kinds() -> None:
    roadmap = read_text("ROADMAP.md")
    federation_payload = json.loads(read_text("generated/federation_entrypoints.min.json"))

    for kind in ("seed", "runtime_surface", "orientation_surface"):
        assert kind in federation_payload["active_entry_kinds"]
        assert f"`{kind}`" in roadmap
