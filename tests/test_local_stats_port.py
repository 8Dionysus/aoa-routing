from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


def test_reference_ratio_matches_current_stats_regrounding_hints() -> None:
    hints = load_json("generated/stats_regrounding_hints.min.json")["hints"]
    packet = load_json("stats/packets/stats-regrounding-owner-first-route-ratio.reference.json")

    owner_first = [hint for hint in hints if hint["primary_action"]["target_repo"] != "aoa-stats"]
    stats_first = [hint for hint in hints if hint["primary_action"]["target_repo"] == "aoa-stats"]

    assert len(hints) == 22
    assert len(owner_first) == 19
    assert {hint["surface_name"] for hint in stats_first} == {
        "object_summary",
        "repeated_window_summary",
        "source_coverage_summary",
    }
    assert packet["population"]["size"] == len(hints)
    assert packet["sample"]["size"] == len(hints)
    assert packet["value"]["numerator"] == len(owner_first)
    assert packet["value"]["denominator"] == len(hints)
    assert packet["value"]["number"] == len(owner_first) / len(hints)
    assert packet["progress"] == {"state": "terminal", "completed": len(hints), "total": len(hints)}
