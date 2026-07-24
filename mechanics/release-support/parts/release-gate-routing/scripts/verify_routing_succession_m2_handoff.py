#!/usr/bin/env python3
"""Verify the fail-closed predecessor side of the M2 owner handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PART_ROOT.parents[3]
EVIDENCE_PATH = (
    PART_ROOT / "evidence" / "routing-succession-m2-conditional-handoff.json"
)
SCHEMA_PATH = (
    PART_ROOT
    / "schemas"
    / "routing-succession-m2-conditional-handoff.schema.json"
)
M1_PIN_PATH = PART_ROOT / "config" / "sdk_shadow_release_pin.json"
DECISION_PATH = (
    REPO_ROOT
    / "docs"
    / "decisions"
    / "AOA-RT-D-0004-stage-producer-succession-to-aoa-sdk.md"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Admit the exact SDK G4 shadow evidence while keeping aoa-routing "
            "canonical until a separate G5 receipt."
        )
    )
    parser.add_argument("--sdk-g4-root", type=Path, required=True)
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return payload


def load_evidence() -> dict[str, Any]:
    evidence = _read_json(EVIDENCE_PATH)
    schema = _read_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(evidence),
        key=lambda error: list(error.path),
    )
    if errors:
        rendered = "; ".join(
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: "
            f"{error.message}"
            for error in errors
        )
        raise RuntimeError(f"invalid M2 conditional handoff evidence: {rendered}")
    return evidence


def _run(
    command: list[str],
    cwd: Path,
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def _git_output(root: Path, *args: str) -> str:
    return _run(["git", *args], root).stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_predecessor_posture(evidence: dict[str, Any]) -> str:
    pin = evidence["pins"]["predecessor"]
    for ref_name in ("implementation_baseline_ref", "m1_parity_consumer_ref"):
        ref = pin[ref_name]
        _run(["git", "cat-file", "-e", f"{ref}^{{commit}}"], REPO_ROOT)
        ancestry = _run(
            ["git", "merge-base", "--is-ancestor", ref, "HEAD"],
            REPO_ROOT,
            check=False,
        )
        if ancestry.returncode != 0:
            raise RuntimeError(f"predecessor history does not contain {ref_name}")

    comparison = _run(
        [
            "git",
            "diff",
            "--quiet",
            pin["implementation_baseline_ref"],
            "--",
            *pin["producer_paths"],
        ],
        REPO_ROOT,
        check=False,
    )
    if comparison.returncode == 1:
        raise RuntimeError(
            "rollback producer changed after the accepted implementation baseline"
        )
    if comparison.returncode != 0:
        raise RuntimeError("unable to compare predecessor rollback producer paths")

    decision = DECISION_PATH.read_text(encoding="utf-8")
    required_decision_markers = (
        "`aoa-routing` remains the sole\ncanonical producer",
        "After G5:",
        "requires a separate exact operator approval",
    )
    missing = [marker for marker in required_decision_markers if marker not in decision]
    if missing:
        raise RuntimeError("paired predecessor decision no longer preserves G5 bounds")
    return _git_output(REPO_ROOT, "rev-parse", "HEAD")


def _require_sdk_g4(
    sdk_root: Path,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    sdk_root = sdk_root.resolve()
    pin = evidence["pins"]["sdk_g4"]
    status = _git_output(sdk_root, "status", "--porcelain", "--untracked-files=normal")
    if status:
        raise RuntimeError("SDK G4 checkout must be clean")
    if _git_output(sdk_root, "rev-parse", "HEAD") != pin["merge_ref"]:
        raise RuntimeError("SDK G4 checkout is not at the admitted merge ref")

    g4_path = sdk_root / pin["evidence_path"]
    if not g4_path.is_file():
        raise RuntimeError("SDK G4 checkout is missing the admitted evidence")
    if _sha256(g4_path) != pin["evidence_sha256"]:
        raise RuntimeError("SDK G4 evidence hash drifted")

    g4 = _read_json(g4_path)
    if g4.get("status") != pin["admitted_status"]:
        raise RuntimeError("SDK G4 evidence status drifted")
    if g4.get("scope", {}).get("canonical_producer") != "aoa-routing":
        raise RuntimeError("SDK G4 evidence no longer keeps the predecessor canonical")
    if g4.get("pins", {}).get("sdk_release", {}).get("source_ref") != pin[
        "release_source_ref"
    ]:
        raise RuntimeError("SDK G4 release source ref drifted")
    if g4.get("pins", {}).get("sdk_release", {}).get("tag") != pin["release_tag"]:
        raise RuntimeError("SDK G4 release tag drifted")
    gate = g4.get("gate_g4", {})
    required_true = (
        "byte_parity",
        "schema_parity",
        "deterministic_generation",
        "package_install",
        "runtime_mirror_content_dry_run",
        "package_trust_chain",
        "predecessor_consumer",
        "rollback_reproducible",
    )
    if gate.get("verdict") != "pass" or any(
        gate.get(field) is not True for field in required_true
    ):
        raise RuntimeError("SDK G4 evidence is incomplete")
    required_false = (
        "runtime_native_sdk_identity",
        "live_runtime_verified_current",
        "canonical_producer_switch_authorized",
        "runtime_publication_authorized",
        "g5_owner_switch",
        "repository_archive_authorized",
    )
    if any(gate.get(field) is not False for field in required_false):
        raise RuntimeError("SDK G4 evidence escalates authority beyond shadow mode")

    local_pin_hash = _sha256(M1_PIN_PATH)
    recorded_pin_hash = g4.get("pins", {}).get("predecessor", {}).get(
        "release_pin_sha256"
    )
    if local_pin_hash != recorded_pin_hash:
        raise RuntimeError("predecessor M1 release pin no longer matches SDK G4")
    return g4


def verify(sdk_g4_root: Path) -> dict[str, Any]:
    evidence = load_evidence()
    current_predecessor_ref = _require_predecessor_posture(evidence)
    g4 = _require_sdk_g4(sdk_g4_root, evidence)
    gates = evidence["gates"]
    return {
        "schema_version": evidence["schema_version"],
        "status": evidence["status"],
        "current_predecessor_ref": current_predecessor_ref,
        "canonical_producer": evidence["scope"]["canonical_producer"],
        "sdk_g4_merge_ref": evidence["pins"]["sdk_g4"]["merge_ref"],
        "sdk_g4_status": g4["status"],
        "feature_acceptance_before_g5": evidence["feature_acceptance"]["before_g5"],
        "compatibility_window": evidence["compatibility_window"]["state"],
        "g5_owner_switch": gates["g5_owner_switch"],
        "predecessor_maintenance_only": gates["predecessor_maintenance_only"],
        "live_runtime_sdk_provenance_verified": gates[
            "live_runtime_sdk_provenance_verified"
        ],
        "archive_authorized": gates["archive_authorized"],
    }


def main() -> int:
    args = parse_args()
    print(json.dumps(verify(args.sdk_g4_root), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
