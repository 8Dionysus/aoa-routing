#!/usr/bin/env python3
"""Validate the aoa-routing source-home topology."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "routing" / "source_home.manifest.json"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(REPO_ROOT)} must be a JSON object")
    return data


def validate() -> list[str]:
    issues: list[str] = []
    if not MANIFEST.exists():
        return ["routing/source_home.manifest.json is missing"]

    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "aoa_routing_source_home.v1":
        issues.append("routing/source_home.manifest.json has wrong schema_version")
    if manifest.get("source_home") != "routing/":
        issues.append("source_home must be routing/")

    required_root_docs = [
        "routing/AGENTS.md",
        "routing/README.md",
        "routing/core/README.md",
    ]
    for route in required_root_docs:
        if not (REPO_ROOT / route).exists():
            issues.append(f"{route} is missing")

    routes = manifest.get("routes")
    if not isinstance(routes, list) or not routes:
        issues.append("routes must be a non-empty list")
        return issues

    seen: set[str] = set()
    for entry in routes:
        if not isinstance(entry, dict):
            issues.append("route entries must be objects")
            continue
        route_id = entry.get("id")
        path = entry.get("path")
        if not isinstance(route_id, str) or not route_id:
            issues.append("route id must be non-empty")
        elif route_id in seen:
            issues.append(f"duplicate route id: {route_id}")
        else:
            seen.add(route_id)
        if not isinstance(path, str) or not path.startswith("routing/") or not path.endswith("/"):
            issues.append(f"{route_id or '<unknown>'}: path must be a routing/ directory")
        elif not (REPO_ROOT / path).is_dir():
            issues.append(f"{path} directory is missing")
        for key in ("owns", "public_outputs", "former_flat_implementation_surfaces"):
            value = entry.get(key)
            if not isinstance(value, list):
                issues.append(f"{route_id or '<unknown>'}: {key} must be a list")

    if {"core"} - seen:
        missing = sorted({"core"} - seen)
        issues.append(f"missing required source-home routes: {', '.join(missing)}")

    return issues


def main() -> int:
    issues = validate()
    if issues:
        print("Source-home topology validation failed.")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("[ok] source-home topology validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
