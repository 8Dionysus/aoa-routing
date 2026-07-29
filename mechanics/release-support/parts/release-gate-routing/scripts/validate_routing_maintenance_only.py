#!/usr/bin/env python3
"""Validate the fail-closed post-G5 predecessor maintenance posture."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
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
APPROVAL_SCHEMA_PATH = (
    PART_ROOT / "schemas" / "routing-maintenance-approval.schema.json"
)
APPROVAL_ROOT = PART_ROOT / "evidence" / "maintenance-approvals"
MAINTENANCE_PART_PREFIX = (
    "mechanics/release-support/parts/release-gate-routing/"
)
MAINTENANCE_APPROVAL_PREFIX = (
    f"{MAINTENANCE_PART_PREFIX}evidence/maintenance-approvals/"
)
KAG_PORTABLE_INDEX_MANIFEST = "kag/indexes/index_family.manifest.json"
KAG_PORTABLE_INDEX_SHARD_PATTERN = re.compile(
    r"^kag/indexes/shards/(?:anchor|event|event_chunk|source)/"
    r"[0-9a-f]{1,2}\.jsonl$"
)
KAG_BUDGET_RECEIPT_PATTERN = re.compile(
    r"^kag/receipts/index_family_budget/[0-9a-f]{64}\.json$"
)
MAINTENANCE_CONTROL_PATHS = {
    ".github/workflows/repo-validation.yml",
    f"{MAINTENANCE_PART_PREFIX}evidence/"
    "routing-succession-m3-maintenance-only.json",
    f"{MAINTENANCE_PART_PREFIX}schemas/"
    "routing-maintenance-approval.schema.json",
    f"{MAINTENANCE_PART_PREFIX}schemas/"
    "routing-succession-m3-maintenance-only.schema.json",
    f"{MAINTENANCE_PART_PREFIX}scripts/"
    "validate_routing_maintenance_only.py",
    "scripts/release_check.py",
    "scripts/validate_active_legacy_names.py",
}
RETIRED_CONTROL_PATHS = {
    ".github/workflows/compatibility-canary.yml",
}
DOCUMENT_SUFFIXES = {".md", ".rst"}


@dataclass(frozen=True)
class ChangedPath:
    status: str
    path: str
    previous_path: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-ref",
        help=(
            "Git base ref used to reject predecessor development. "
            "Defaults to the immutable maintenance base in the M3 receipt."
        ),
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


def load_approvals() -> tuple[dict[str, Any], ...]:
    if not APPROVAL_ROOT.exists():
        return ()
    schema = _read_json(APPROVAL_SCHEMA_PATH)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    approvals: list[dict[str, Any]] = []
    approval_ids: set[str] = set()
    for path in sorted(APPROVAL_ROOT.glob("*.json")):
        approval = _read_json(path)
        errors = sorted(
            validator.iter_errors(approval),
            key=lambda error: list(error.path),
        )
        if errors:
            rendered = "; ".join(
                f"{'/'.join(str(part) for part in error.path) or '<root>'}: "
                f"{error.message}"
                for error in errors
            )
            raise RuntimeError(
                f"invalid routing maintenance approval {path}: {rendered}"
            )
        approval_id = approval["approval_id"]
        if approval_id in approval_ids:
            raise RuntimeError(
                f"duplicate routing maintenance approval_id: {approval_id}"
            )
        approval_ids.add(approval_id)
        approvals.append(approval)
    return tuple(approvals)


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def _changed_entries(base_ref: str) -> tuple[ChangedPath, ...]:
    completed = _git(
        "diff",
        "--name-status",
        "--find-renames",
        "--diff-filter=ACDMRTUXB",
        f"{base_ref}...HEAD",
    )
    entries: list[ChangedPath] = []
    for line in completed.stdout.splitlines():
        if not line:
            continue
        fields = line.split("\t")
        status = fields[0]
        status_code = status[:1]
        if status_code in {"C", "R"}:
            if len(fields) != 3:
                raise RuntimeError(f"unparseable Git change record: {line!r}")
            entries.append(
                ChangedPath(
                    status=status,
                    previous_path=fields[1],
                    path=fields[2],
                )
            )
        else:
            if len(fields) != 2:
                raise RuntimeError(f"unparseable Git change record: {line!r}")
            entries.append(ChangedPath(status=status, path=fields[1]))
    return tuple(entries)


def _changed_paths(base_ref: str) -> tuple[str, ...]:
    return tuple(entry.path for entry in _changed_entries(base_ref))


def _workflow_paths(workflow_root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            {
                *workflow_root.glob("*.yml"),
                *workflow_root.glob("*.yaml"),
            }
        )
    )


def _is_document_or_test_path(path: str) -> bool:
    candidate = Path(path)
    return path.startswith("tests/") or candidate.suffix in DOCUMENT_SUFFIXES


def _is_maintenance_control_path(path: str) -> bool:
    approval_path = Path(path)
    return (
        path in MAINTENANCE_CONTROL_PATHS
        or KAG_BUDGET_RECEIPT_PATTERN.fullmatch(path) is not None
        or (
            path.startswith(MAINTENANCE_APPROVAL_PREFIX)
            and approval_path.parent.as_posix()
            == MAINTENANCE_APPROVAL_PREFIX.rstrip("/")
            and approval_path.suffix == ".json"
        )
    )


def _is_kag_portable_index_path(path: str) -> bool:
    return (
        path == KAG_PORTABLE_INDEX_MANIFEST
        or KAG_PORTABLE_INDEX_SHARD_PATTERN.fullmatch(path) is not None
    )


def _is_generated_output(path: str) -> bool:
    return (
        path.startswith("generated/")
        or "/generated/" in path
    ) and not path.startswith("tests/")


def _is_retained_implementation_path(path: str) -> bool:
    # In maintenance-only mode every other non-document, non-test,
    # non-control artifact is implementation state. Unknown paths must not
    # become an implicit feature or publication escape hatch.
    return not (
        _is_document_or_test_path(path)
        or _is_maintenance_control_path(path)
    )


def _head_blob_id(path: str) -> str:
    return _git("rev-parse", f"HEAD:{path}").stdout.strip()


def _approval_coverage(
    approvals: tuple[dict[str, Any], ...],
    *,
    evidence: dict[str, Any],
    base_ref: str,
) -> dict[str, set[str]]:
    allowed_classes = set(
        evidence["scope"]["allowed_predecessor_change_classes"]
    )
    coverage: dict[str, set[str]] = {}
    for approval in approvals:
        change_class = approval["change_class"]
        if change_class not in allowed_classes:
            raise RuntimeError(
                "routing maintenance approval uses a disallowed class: "
                f"{change_class}"
            )
        approval_base_ref = approval["scope"]["maintenance_base_ref"]
        if approval_base_ref != base_ref:
            raise RuntimeError(
                "routing maintenance approval uses the wrong maintenance base: "
                f"{approval['approval_id']}={approval_base_ref}, expected={base_ref}"
            )
        for item in approval["scope"]["retained_source_blobs"]:
            path = item["path"]
            if (
                _is_generated_output(path)
                or not _is_retained_implementation_path(path)
            ):
                raise RuntimeError(
                    "routing maintenance approval cannot cover generated, "
                    f"document, test, or maintenance-control path: {path}"
                )
            coverage.setdefault(path, set()).add(item["git_blob_id"])
    return coverage


def _validate_change_boundary(
    entries: tuple[ChangedPath, ...],
    approvals: tuple[dict[str, Any], ...],
    *,
    evidence: dict[str, Any],
    base_ref: str,
    blob_resolver: Any = None,
) -> tuple[str, ...]:
    resolve_blob = blob_resolver or _head_blob_id
    approval_coverage = _approval_coverage(
        approvals,
        evidence=evidence,
        base_ref=base_ref,
    )
    forbidden: list[str] = []
    unapproved: list[str] = []
    approved: list[str] = []

    for entry in entries:
        status_code = entry.status[:1]
        paths = tuple(
            path
            for path in (entry.previous_path, entry.path)
            if path is not None
        )
        portable_index_paths = tuple(
            path for path in paths if _is_kag_portable_index_path(path)
        )
        if portable_index_paths:
            if (
                status_code == "M"
                and len(portable_index_paths) == len(paths)
            ):
                continue
            forbidden.append(f"{entry.status}:{' -> '.join(paths)}")
            continue
        if any(_is_generated_output(path) for path in paths):
            forbidden.append(f"{entry.status}:{' -> '.join(paths)}")
            continue
        if (
            status_code == "D"
            and entry.path in RETIRED_CONTROL_PATHS
        ):
            continue
        if all(
            _is_document_or_test_path(path)
            or _is_maintenance_control_path(path)
            for path in paths
        ):
            continue

        retained_paths = [
            path for path in paths if _is_retained_implementation_path(path)
        ]
        if status_code in {"A", "C", "D", "R", "T", "U", "X", "B"}:
            forbidden.append(f"{entry.status}:{' -> '.join(paths)}")
            continue
        if status_code != "M" or not retained_paths:
            continue

        path = entry.path
        blob_id = resolve_blob(path)
        if blob_id not in approval_coverage.get(path, set()):
            unapproved.append(f"{path}@{blob_id}")
        else:
            approved.append(path)

    if forbidden:
        raise RuntimeError(
            "new, structural, or generated predecessor implementation changes "
            "belong in aoa-sdk after G5: "
            + ", ".join(sorted(forbidden))
        )
    if unapproved:
        raise RuntimeError(
            "retained predecessor source changes require an exact reviewed "
            "maintenance approval packet: "
            + ", ".join(sorted(unapproved))
        )
    return tuple(sorted(approved))


def validate(base_ref: str | None = None) -> dict[str, Any]:
    evidence = load_evidence()
    rollback_ref = evidence["pins"]["predecessor"]["rollback_implementation_ref"]
    _git("cat-file", "-e", f"{rollback_ref}^{{commit}}")
    effective_base_ref = (
        base_ref
        or evidence["pins"]["predecessor"]["maintenance_base_ref"]
    )
    _git("cat-file", "-e", f"{effective_base_ref}^{{commit}}")

    workflow_root = REPO_ROOT / ".github" / "workflows"
    workflow_paths = _workflow_paths(workflow_root)
    workflows = [path.name for path in workflow_paths]
    workflow = "\n".join(
        path.read_text(encoding="utf-8") for path in workflow_paths
    )
    if workflows != ["repo-validation.yml"]:
        raise RuntimeError(
            "maintenance-only predecessor must expose exactly Repo Validation"
        )
    forbidden_workflow_markers = (
        "repository: 8Dionysus/",
        "build_router.py",
        "validate_router.py",
        "aoa-sdk",
        "Compatibility Canary",
        "gh release",
        "publish",
        "twine upload",
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
        "gh release",
        "publish",
        "twine upload",
    )
    present = [
        marker for marker in forbidden_release_markers if marker in release_check
    ]
    if present:
        raise RuntimeError(
            f"maintenance release gate retains producer work: {present}"
        )

    changed_entries = _changed_entries(effective_base_ref)
    approved_paths = _validate_change_boundary(
        changed_entries,
        load_approvals(),
        evidence=evidence,
        base_ref=effective_base_ref,
    )
    changed_paths = tuple(entry.path for entry in changed_entries)

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
        "maintenance_base_ref": effective_base_ref,
        "changed_path_count": len(changed_paths),
        "approved_retained_source_paths": list(approved_paths),
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
