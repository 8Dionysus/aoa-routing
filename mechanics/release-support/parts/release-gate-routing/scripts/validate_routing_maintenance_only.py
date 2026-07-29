#!/usr/bin/env python3
"""Validate the fail-closed post-G5 predecessor maintenance posture."""

from __future__ import annotations

import argparse
import copy
import hashlib
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
KAG_PORTABLE_SCHEMA_VERSION = "aoa-repo-local-kag-family-manifest-v3"
KAG_BUDGET_RECEIPT_SCHEMA_VERSION = "aoa-repo-local-kag-budget-receipt-v1"
KAG_ARCHIVE_APPROVAL_REF = (
    "operator-confirmation:github-repository-1186624390:2026-07-29"
)
KAG_ARCHIVE_APPROVAL_SCOPE = "final-v0.4.0-archive-refresh-only"
KAG_ARCHIVE_TARGET_REPOSITORY_ID = 1186624390
ZERO_DIGEST = "0" * 64
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


def _is_kag_budget_receipt_path(path: str) -> bool:
    return KAG_BUDGET_RECEIPT_PATTERN.fullmatch(path) is not None


def _is_kag_portable_index_path(path: str) -> bool:
    return (
        path == KAG_PORTABLE_INDEX_MANIFEST
        or KAG_PORTABLE_INDEX_SHARD_PATTERN.fullmatch(path) is not None
    )


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _portable_manifest_digest(manifest: dict[str, Any]) -> str:
    candidate = copy.deepcopy(manifest)
    identity = candidate.get("family_identity")
    if not isinstance(identity, dict):
        raise RuntimeError("portable KAG manifest needs family_identity")
    identity["content_digest"] = ZERO_DIGEST
    return hashlib.sha256(_canonical_json_bytes(candidate)).hexdigest()


def _git_bytes_at_ref(ref: str, path: str) -> bytes | None:
    exists = _git("cat-file", "-e", f"{ref}:{path}", check=False)
    if exists.returncode != 0:
        return None
    completed = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def _portable_paths_at_ref(ref: str) -> set[str]:
    completed = _git(
        "ls-tree",
        "-r",
        "--name-only",
        ref,
        "--",
        "kag/indexes",
    )
    return {
        path
        for path in completed.stdout.splitlines()
        if _is_kag_portable_index_path(path)
    }


def _validate_kag_portable_index_integrity() -> str:
    manifest_path = REPO_ROOT / KAG_PORTABLE_INDEX_MANIFEST
    manifest = _read_json(manifest_path)
    if manifest.get("schema_version") != KAG_PORTABLE_SCHEMA_VERSION:
        raise RuntimeError("portable KAG manifest schema version drifted")

    identity = manifest.get("family_identity")
    if not isinstance(identity, dict):
        raise RuntimeError("portable KAG manifest needs family_identity")
    family_digest = identity.get("content_digest")
    if (
        not isinstance(family_digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", family_digest) is None
        or family_digest != _portable_manifest_digest(manifest)
    ):
        raise RuntimeError("portable KAG manifest digest does not match")

    shards = manifest.get("shards")
    summary = manifest.get("summary")
    budgets = manifest.get("budgets")
    if (
        not isinstance(shards, list)
        or not isinstance(summary, dict)
        or not isinstance(budgets, dict)
    ):
        raise RuntimeError("portable KAG manifest is incomplete")

    expected_paths: set[str] = set()
    shard_bytes = 0
    record_counts: dict[str, int] = {}
    canonical_records = 0
    source_blobs: dict[str, str] = {}
    for descriptor in shards:
        if not isinstance(descriptor, dict):
            raise RuntimeError("portable KAG shard descriptor must be an object")
        kind = descriptor.get("kind")
        shard_range = descriptor.get("range")
        relative = descriptor.get("path")
        if (
            not isinstance(kind, str)
            or not isinstance(shard_range, str)
            or not isinstance(relative, str)
            or relative
            != f"kag/indexes/shards/{kind}/{shard_range}.jsonl"
            or not _is_kag_portable_index_path(relative)
            or relative in expected_paths
        ):
            raise RuntimeError("portable KAG shard path is invalid or duplicated")
        expected_paths.add(relative)
        content = (REPO_ROOT / relative).read_bytes()
        if descriptor.get("digest") != (
            f"sha256:{hashlib.sha256(content).hexdigest()}"
        ):
            raise RuntimeError(
                f"portable KAG shard digest does not match: {relative}"
            )
        if descriptor.get("bytes") != len(content):
            raise RuntimeError(
                f"portable KAG shard byte count does not match: {relative}"
            )
        rows = content.splitlines()
        if descriptor.get("records") != len(rows):
            raise RuntimeError(
                f"portable KAG shard record count does not match: {relative}"
            )
        for line_number, line in enumerate(rows, start=1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"{relative}:{line_number} is not valid JSON"
                ) from exc
            if not isinstance(row, dict) or row.get("_kind") != kind:
                raise RuntimeError(
                    f"{relative}:{line_number} record kind does not match"
                )
            if kind == "source":
                row_identity = row.get("identity")
                if not isinstance(row_identity, dict):
                    raise RuntimeError(
                        f"{relative}:{line_number} source identity is missing"
                    )
                source_path = row_identity.get("path")
                source_blob = row_identity.get("git_blob_id")
                if (
                    not isinstance(source_path, str)
                    or not isinstance(source_blob, str)
                    or source_path in source_blobs
                ):
                    raise RuntimeError(
                        f"{relative}:{line_number} source identity is invalid"
                    )
                source_blobs[source_path] = source_blob
        record_counts[kind] = record_counts.get(kind, 0) + len(rows)
        canonical_records += len(rows)
        shard_bytes += len(content)

    actual_paths = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "kag" / "indexes" / "shards").rglob(
            "*.jsonl"
        )
    }
    if actual_paths != expected_paths:
        raise RuntimeError("portable KAG shard inventory does not match manifest")

    tracked_paths = set(_git("ls-files").stdout.splitlines())
    expected_source_paths = {
        path
        for path in tracked_paths
        if not _is_kag_portable_index_path(path)
        and not _is_kag_budget_receipt_path(path)
    }
    if set(source_blobs) != expected_source_paths:
        raise RuntimeError(
            "portable KAG source inventory does not match tracked source tree"
        )
    approved_source_rows: list[dict[str, str]] = []
    for source_path in sorted(source_blobs):
        head_blob = _head_blob_id(source_path)
        if source_blobs[source_path] != head_blob:
            raise RuntimeError(
                "portable KAG source blob does not match HEAD: "
                f"{source_path}"
            )
        approved_source_rows.append(
            {
                "path": source_path,
                "git_blob_id": head_blob,
            }
        )
    source_tree_digest = hashlib.sha256(
        _canonical_json_bytes(approved_source_rows)
    ).hexdigest()

    if (
        summary.get("shards") != len(shards)
        or summary.get("shard_bytes") != shard_bytes
        or summary.get("canonical_records") != canonical_records
        or summary.get("source_records") != record_counts.get("source", 0)
        or summary.get("anchor_records") != record_counts.get("anchor", 0)
        or summary.get("event_records") != record_counts.get("event", 0)
        or summary.get("tracked_bytes")
        != len(manifest_path.read_bytes()) + shard_bytes
    ):
        raise RuntimeError("portable KAG manifest summary does not match corpus")

    receipt_relative = (
        "kag/receipts/index_family_budget/" f"{family_digest}.json"
    )
    receipt = _read_json(REPO_ROOT / receipt_relative)
    base_ref = receipt.get("base_ref")
    if not isinstance(base_ref, str):
        raise RuntimeError("portable KAG budget receipt needs a base_ref")
    resolved_base = _git("rev-parse", base_ref).stdout.strip()
    if resolved_base != base_ref:
        raise RuntimeError("portable KAG budget receipt base_ref is not immutable")

    head_paths = {KAG_PORTABLE_INDEX_MANIFEST, *expected_paths}
    base_paths = _portable_paths_at_ref(base_ref)
    changed_bytes = 0
    changed_files = 0
    for relative in sorted(head_paths | base_paths):
        old = _git_bytes_at_ref(base_ref, relative)
        current_path = REPO_ROOT / relative
        new = current_path.read_bytes() if current_path.is_file() else None
        if old == new:
            continue
        changed_files += 1
        changed_bytes += max(len(old or b""), len(new or b""))

    expected_receipt = {
        "schema_version": KAG_BUDGET_RECEIPT_SCHEMA_VERSION,
        "repo": manifest.get("repo", {}).get("name"),
        "base_ref": base_ref,
        "head_family_digest": family_digest,
        "changed_generated_bytes": changed_bytes,
        "changed_generated_files": changed_files,
        "default_limit_bytes": budgets.get("changed_generated_bytes_max"),
        "tracked_bytes": summary.get("tracked_bytes"),
        "tracked_bytes_max": budgets.get("tracked_bytes_max"),
        "approval_ref": KAG_ARCHIVE_APPROVAL_REF,
        "approval_scope": KAG_ARCHIVE_APPROVAL_SCOPE,
        "archive_target_repository_id": KAG_ARCHIVE_TARGET_REPOSITORY_ID,
        "approved_family_digest": family_digest,
        "approved_source_tree_digest": source_tree_digest,
    }
    mismatched = [
        field
        for field, expected in expected_receipt.items()
        if receipt.get(field) != expected
    ]
    if mismatched:
        raise RuntimeError(
            "portable KAG budget receipt does not match current family: "
            + ", ".join(mismatched)
        )
    if (
        receipt.get("approved_by") != "repository operator"
        or not isinstance(receipt.get("reason"), str)
        or not receipt["reason"].strip()
        or receipt.get("allowed_bytes", -1) < changed_bytes
        or receipt.get("allowed_tracked_bytes", -1)
        < summary["tracked_bytes"]
    ):
        raise RuntimeError("portable KAG budget receipt approval is incomplete")
    return family_digest


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
    portable_family_digest: str | None = None,
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
                and portable_family_digest is not None
            ):
                continue
            forbidden.append(f"{entry.status}:{' -> '.join(paths)}")
            continue
        budget_receipt_paths = tuple(
            path for path in paths if _is_kag_budget_receipt_path(path)
        )
        if budget_receipt_paths:
            expected_receipt = (
                "kag/receipts/index_family_budget/"
                f"{portable_family_digest}.json"
            )
            if (
                status_code == "A"
                and len(budget_receipt_paths) == len(paths)
                and entry.path == expected_receipt
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

    portable_family_digest = _validate_kag_portable_index_integrity()
    changed_entries = _changed_entries(effective_base_ref)
    approved_paths = _validate_change_boundary(
        changed_entries,
        load_approvals(),
        evidence=evidence,
        base_ref=effective_base_ref,
        portable_family_digest=portable_family_digest,
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
        "portable_kag_family_digest": portable_family_digest,
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
