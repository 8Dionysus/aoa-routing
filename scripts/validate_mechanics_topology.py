#!/usr/bin/env python3
"""Validate aoa-routing mechanics topology surfaces."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = REPO_ROOT / "mechanics" / "topology.json"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
REQUIRED_PARENT_FILES = (
    "AGENTS.md",
    "README.md",
    "PARTS.md",
    "PROVENANCE.md",
    "ROADMAP.md",
)
REQUIRED_ROADMAP_HEADINGS = (
    "## Current Contour",
    "## Next Work",
    "## When Time Comes",
    "## Out Of Scope",
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(REPO_ROOT)} must be a JSON object")
    return data


def validate() -> list[str]:
    issues: list[str] = []
    for route in ("mechanics/AGENTS.md", "mechanics/README.md", "mechanics/topology.json"):
        if not (REPO_ROOT / route).exists():
            issues.append(f"{route} is missing")
    if issues or not TOPOLOGY.exists():
        return issues

    topology = load_json(TOPOLOGY)
    if topology.get("schema_version") != "aoa_routing_mechanics_topology.v1":
        issues.append("mechanics/topology.json has wrong schema_version")

    parents = topology.get("parents")
    if not isinstance(parents, list) or not parents:
        issues.append("parents must be a non-empty list")
        return issues

    parent_ids: set[str] = set()
    for parent in parents:
        if not isinstance(parent, dict):
            issues.append("parent entries must be objects")
            continue
        parent_id = parent.get("id")
        if not isinstance(parent_id, str) or not SLUG_RE.match(parent_id):
            issues.append(f"invalid parent id: {parent_id!r}")
            continue
        if parent_id in parent_ids:
            issues.append(f"duplicate parent id: {parent_id}")
        parent_ids.add(parent_id)
        parent_root = REPO_ROOT / "mechanics" / parent_id
        for filename in REQUIRED_PARENT_FILES:
            route = parent_root / filename
            if not route.exists():
                issues.append(f"mechanics/{parent_id}/{filename} is missing")
        roadmap_path = parent_root / "ROADMAP.md"
        if roadmap_path.exists():
            roadmap_text = roadmap_path.read_text(encoding="utf-8")
            first_line = roadmap_text.splitlines()[0] if roadmap_text.splitlines() else ""
            if not first_line.startswith("# ") or "Roadmap" not in first_line:
                issues.append(f"mechanics/{parent_id}/ROADMAP.md must start with a mechanic roadmap heading")
            for heading in REQUIRED_ROADMAP_HEADINGS:
                if heading not in roadmap_text:
                    issues.append(f"mechanics/{parent_id}/ROADMAP.md is missing {heading}")
        parts = parent.get("parts")
        if not isinstance(parts, list) or not parts:
            issues.append(f"{parent_id}: parts must be a non-empty list")
            continue
        seen_parts: set[str] = set()
        for part in parts:
            if not isinstance(part, str) or not SLUG_RE.match(part):
                issues.append(f"{parent_id}: invalid part id {part!r}")
                continue
            if part in seen_parts:
                issues.append(f"{parent_id}: duplicate part id {part}")
            seen_parts.add(part)

    required = {
        "agon",
        "experience",
        "checkpoint",
        "recurrence",
        "questbook",
        "boundary-bridge",
        "governance",
        "antifragility",
        "release-support",
        "titan",
        "rpg",
    }
    missing = sorted(required - parent_ids)
    if missing:
        issues.append(f"missing required evidenced parents: {', '.join(missing)}")

    return issues


def main() -> int:
    issues = validate()
    if issues:
        print("Mechanics topology validation failed.")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("[ok] mechanics topology validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
