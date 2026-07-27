#!/usr/bin/env python3
"""Validate the fail-closed post-G5 predecessor maintenance posture."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PART_ROOT.parents[3]
EVIDENCE_PATH = (
    PART_ROOT / "evidence" / "routing-succession-m3-maintenance-only.json"
)
SCHEMA_PATH = (
    PART_ROOT / "schemas" / "routing-succession-m3-maintenance-only.schema.json"
)
PRODUCER_PATH_PREFIXES = (
    "generated/",
    "routing/core/",
    "schemas/",
)
PRODUCER_PATHS = {
    "routing/source_home.manifest.json",
    "scripts/build_router.py",
    "scripts/router_core.py",
    "scripts/validate_router.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-ref",
        help="Optional Git base ref used to reject new producer changes.",
    )
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return payload


def load_evidence() -> dict[str, Any]:
    evidence = _read_json(EVIDENCE_PATH)
    schema = _read_json(SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(evidence),
        key=lambda error: list(error.path),
    )
    if errors:
        rendered = "; ".join(
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: "
            f"{error.message}"
            for error in errors
        )
        raise RuntimeError(f"invalid M3 maintenance-only evidence: {rendered}")
    return evidence


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def _changed_paths(base_ref: str) -> tuple[str, ...]:
    completed = _git(
        "diff",
        "--name-only",
        "--diff-filter=ACMRTUXB",
        f"{base_ref}...HEAD",
    )
    return tuple(line for line in completed.stdout.splitlines() if line)


def _is_producer_path(path: str) -> bool:
    return path in PRODUCER_PATHS or path.startswith(PRODUCER_PATH_PREFIXES)


def validate(base_ref: str | None = None) -> dict[str, Any]:
    evidence = load_evidence()
    rollback_ref = evidence["pins"]["predecessor"]["rollback_implementation_ref"]
    _git("cat-file", "-e", f"{rollback_ref}^{{commit}}")

    workflow_root = REPO_ROOT / ".github" / "workflows"
    workflows = sorted(path.name for path in workflow_root.glob("*.yml"))
    if workflows != ["repo-validation.yml"]:
        raise RuntimeError(
            "maintenance-only predecessor must expose exactly Repo Validation"
        )
    workflow = (workflow_root / "repo-validation.yml").read_text(encoding="utf-8")
    forbidden_workflow_markers = (
        "repository: 8Dionysus/",
        "build_router.py",
        "validate_router.py",
        "aoa-sdk",
        "Compatibility Canary",
    )
    present = [marker for marker in forbidden_workflow_markers if marker in workflow]
    if present:
        raise RuntimeError(
            f"maintenance workflow retains active producer dependencies: {present}"
        )

    release_check = (REPO_ROOT / "scripts" / "release_check.py").read_text(
        encoding="utf-8"
    )
    forbidden_release_markers = (
        "build_router",
        "validate_router",
        "sdk_shadow",
        "AOA_SDK",
        "abyss_machine_routing_bundle",
    )
    present = [
        marker for marker in forbidden_release_markers if marker in release_check
    ]
    if present:
        raise RuntimeError(
            f"maintenance release gate retains producer work: {present}"
        )

    changed_paths: tuple[str, ...] = ()
    if base_ref is not None:
        changed_paths = _changed_paths(base_ref)
        producer_changes = sorted(
            path for path in changed_paths if _is_producer_path(path)
        )
        if producer_changes:
            raise RuntimeError(
                "new routing producer changes belong in aoa-sdk after G5: "
                + ", ".join(producer_changes)
            )

    gates = evidence["gates"]
    if gates["archive_ready"] or gates["archive_authorized"]:
        raise RuntimeError("maintenance posture cannot authorize archive")

    return {
        "schema_version": evidence["schema_version"],
        "status": evidence["status"],
        "canonical_producer": evidence["scope"]["canonical_producer"],
        "workflow_contours": len(workflows),
        "sibling_checkouts": 0,
        "producer_generation_in_ci": False,
        "changed_path_count": len(changed_paths),
        "consumer_zero": gates["consumer_zero"],
        "archive_ready": gates["archive_ready"],
        "archive_authorized": gates["archive_authorized"],
    }


def main() -> int:
    args = parse_args()
    print(json.dumps(validate(args.base_ref), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
