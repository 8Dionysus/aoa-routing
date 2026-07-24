#!/usr/bin/env python3
"""Fail-closed predecessor consumer for the pinned aoa-sdk M1 shadow release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import venv
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PART_ROOT.parents[3]
PIN_PATH = PART_ROOT / "config" / "sdk_shadow_release_pin.json"
PIN_SCHEMA_PATH = PART_ROOT / "schemas" / "sdk-shadow-release-pin.schema.json"
PROBE_PATH = Path(__file__).with_name("sdk_shadow_release_probe.py")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install the exact pinned aoa-sdk release and compare its shadow "
            "producer with the unchanged canonical aoa-routing producer."
        )
    )
    parser.add_argument("--sdk-root", type=Path, required=True)
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return payload


def load_pin() -> dict[str, Any]:
    pin = _read_json(PIN_PATH)
    schema = _read_json(PIN_SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(pin), key=lambda error: list(error.path))
    if errors:
        rendered = "; ".join(
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: "
            f"{error.message}"
            for error in errors
        )
        raise RuntimeError(f"invalid SDK shadow release pin: {rendered}")
    return pin


def _run(
    command: list[str],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        capture_output=capture_output,
        text=True,
    )


def _git_output(root: Path, *args: str) -> str:
    return _run(
        ["git", *args],
        root,
        capture_output=True,
    ).stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_sdk_release_checkout(sdk_root: Path, pin: dict[str, Any]) -> None:
    release = pin["sdk_release"]
    status = _git_output(sdk_root, "status", "--porcelain", "--untracked-files=normal")
    if status:
        raise RuntimeError("pinned aoa-sdk release checkout must be clean")
    observed_head = _git_output(sdk_root, "rev-parse", "HEAD")
    if observed_head != release["source_ref"]:
        raise RuntimeError(
            "aoa-sdk release source mismatch: "
            f"expected {release['source_ref']}, observed {observed_head}"
        )
    tag_ref = f"refs/tags/{release['tag']}"
    if _git_output(sdk_root, "cat-file", "-t", tag_ref) != "tag":
        raise RuntimeError(f"aoa-sdk release tag must be annotated: {release['tag']}")
    observed_tag_object = _git_output(sdk_root, "rev-parse", tag_ref)
    if observed_tag_object != release["tag_object_ref"]:
        raise RuntimeError(
            f"aoa-sdk annotated tag object drifted for {release['tag']}"
        )
    observed_tag_target = _git_output(sdk_root, "rev-parse", f"{tag_ref}^{{}}")
    if observed_tag_target != release["source_ref"]:
        raise RuntimeError(
            f"aoa-sdk tag {release['tag']} does not peel to the pinned source ref"
        )
    project = tomllib.loads((sdk_root / "pyproject.toml").read_text(encoding="utf-8"))
    if project.get("project", {}).get("version") != release["version"]:
        raise RuntimeError("aoa-sdk package version does not match the release pin")


def _require_unchanged_predecessor(pin: dict[str, Any]) -> str:
    predecessor = pin["predecessor"]
    baseline = predecessor["implementation_baseline_ref"]
    _run(["git", "cat-file", "-e", f"{baseline}^{{commit}}"], REPO_ROOT)
    comparison = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            baseline,
            "--",
            *predecessor["producer_paths"],
        ],
        cwd=REPO_ROOT,
        check=False,
    )
    if comparison.returncode == 1:
        raise RuntimeError(
            "canonical aoa-routing producer changed after the pinned M1 baseline"
        )
    if comparison.returncode != 0:
        raise RuntimeError("unable to compare canonical predecessor producer paths")
    return _git_output(REPO_ROOT, "rev-parse", "HEAD")


def safe_materialize_fixture(archive_path: Path, target: Path) -> None:
    """Extract only unique regular files and directories beneath target."""

    target.mkdir(parents=True, exist_ok=False)
    seen: set[PurePosixPath] = set()
    with tarfile.open(archive_path, mode="r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            name = PurePosixPath(member.name)
            if name == PurePosixPath("."):
                if not member.isdir():
                    raise RuntimeError("fixture archive root member must be a directory")
                continue
            if (
                name.is_absolute()
                or not name.parts
                or any(part in {"", ".", ".."} for part in name.parts)
            ):
                raise RuntimeError(f"unsafe fixture archive path: {member.name}")
            if name in seen:
                raise RuntimeError(f"duplicate fixture archive path: {member.name}")
            seen.add(name)
            if member.issym() or member.islnk() or not (
                member.isdir() or member.isfile()
            ):
                raise RuntimeError(
                    f"unsupported fixture archive member: {member.name}"
                )
            destination = target.joinpath(*name.parts)
            resolved = destination.resolve()
            if target.resolve() not in resolved.parents:
                raise RuntimeError(f"fixture archive path escapes target: {member.name}")
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"unable to read fixture member: {member.name}")
            with source, destination.open("xb") as output:
                shutil.copyfileobj(source, output)


def _fixture_paths(
    sdk_root: Path,
    pin: dict[str, Any],
) -> tuple[Path, Path]:
    fixture = pin["fixture"]
    archive_path = sdk_root / fixture["archive_path"]
    expected_hashes_path = sdk_root / fixture["expected_hashes_path"]
    if not archive_path.is_file() or not expected_hashes_path.is_file():
        raise RuntimeError("pinned aoa-sdk release is missing routing parity fixtures")
    if _sha256(archive_path) != fixture["archive_sha256"]:
        raise RuntimeError("pinned aoa-sdk routing input archive hash drifted")
    return archive_path, expected_hashes_path


def _common_predecessor_args(fixture_root: Path, output_dir: Path) -> list[str]:
    return [
        "--techniques-root",
        str(fixture_root / "aoa-techniques"),
        "--skills-root",
        str(fixture_root / "aoa-skills"),
        "--evals-root",
        str(fixture_root / "aoa-evals"),
        "--memo-root",
        str(fixture_root / "aoa-memo"),
        "--stats-root",
        str(fixture_root / "aoa-stats"),
        "--agents-root",
        str(fixture_root / "aoa-agents"),
        "--aoa-root",
        str(fixture_root / "Agents-of-Abyss"),
        "--playbooks-root",
        str(fixture_root / "aoa-playbooks"),
        "--kag-root",
        str(fixture_root / "aoa-kag"),
        "--tos-root",
        str(fixture_root / "Tree-of-Sophia"),
        "--sdk-root",
        str(fixture_root / "aoa-sdk"),
        "--source-route-root",
        str(fixture_root / "Dionysus"),
        "--profile-root",
        str(fixture_root / "8Dionysus"),
        "--abyss-stack-root",
        str(fixture_root / "abyss-stack"),
        "--generated-dir",
        str(output_dir),
    ]


def _build_wheel(sdk_root: Path, output_dir: Path, version: str) -> Path:
    _run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--outdir",
            str(output_dir),
        ],
        sdk_root,
    )
    wheels = sorted(output_dir.glob(f"aoa_sdk-{version}-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(
            f"expected one aoa-sdk {version} wheel, found {len(wheels)}"
        )
    return wheels[0]


def _installed_sdk_report(
    wheel: Path,
    sdk_root: Path,
    fixture_root: Path,
    output_dir: Path,
    current_predecessor_ref: str,
    pin: dict[str, Any],
    environment_root: Path,
) -> dict[str, Any]:
    venv.EnvBuilder(with_pip=True, clear=False).create(environment_root)
    python = environment_root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    _run(
        [
            str(python),
            "-m",
            "pip",
            "--disable-pip-version-check",
            "install",
            str(wheel),
        ],
        environment_root.parent,
        env=environment,
    )
    completed = _run(
        [
            str(python),
            str(PROBE_PATH),
            "--fixture-root",
            str(fixture_root),
            "--output-dir",
            str(output_dir),
            "--pin",
            str(PIN_PATH),
            "--sdk-checkout",
            str(sdk_root),
            "--predecessor-source-ref",
            current_predecessor_ref,
        ],
        environment_root.parent,
        env=environment,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def _artifact_hashes(
    root: Path,
    artifact_names: list[str],
    *,
    allowed_extra_entries: set[str] | None = None,
) -> dict[str, str]:
    actual_entries = {path.name for path in root.iterdir()}
    expected_entries = set(artifact_names) | (allowed_extra_entries or set())
    if actual_entries != expected_entries:
        raise RuntimeError(
            "routing artifact set drifted: "
            f"expected={sorted(expected_entries)}, actual={sorted(actual_entries)}"
        )
    return {
        name: _sha256(root / name)
        for name in artifact_names
    }


def _verify_report(
    report: dict[str, Any],
    pin: dict[str, Any],
    current_predecessor_ref: str,
) -> None:
    release = pin["sdk_release"]
    expected = {
        "abi_epoch": pin["abi_epoch"],
        "artifact_count": len(pin["artifact_names"]),
        "package_version": release["version"],
        "publication_posture": "non_publishing",
        "schema_count": 17,
        "sidecar": "routing-shadow-provenance.json",
        "state": "sdk_shadow",
    }
    for field, value in expected.items():
        if report.get(field) != value:
            raise RuntimeError(
                f"installed SDK report field {field!r} drifted: {report.get(field)!r}"
            )
    if report.get("canonical_producer") != {
        "owner_repo": "aoa-routing",
        "source_ref": current_predecessor_ref,
    }:
        raise RuntimeError("installed SDK canonical-producer provenance drifted")
    if report.get("shadow_producer") != {
        "implementation": "aoa_sdk.control_plane.routing",
        "owner_repo": "aoa-sdk",
        "source_ref": release["source_ref"],
    }:
        raise RuntimeError("installed SDK shadow-producer provenance drifted")
    if report.get("input_source_refs") != pin["fixture"]["input_source_refs"]:
        raise RuntimeError("installed SDK input provenance drifted")


def main() -> int:
    args = parse_args()
    sdk_root = args.sdk_root.resolve()
    pin = load_pin()
    _require_sdk_release_checkout(sdk_root, pin)
    current_predecessor_ref = _require_unchanged_predecessor(pin)
    archive_path, expected_hashes_path = _fixture_paths(sdk_root, pin)

    with tempfile.TemporaryDirectory(
        prefix="aoa-routing-sdk-release-parity-"
    ) as temporary:
        root = Path(temporary)
        fixture_root = root / "fixture"
        safe_materialize_fixture(archive_path, fixture_root)
        predecessor_output = root / "predecessor"
        sdk_output = root / "sdk-shadow"
        wheel = _build_wheel(
            sdk_root,
            root / "dist",
            pin["sdk_release"]["version"],
        )
        _run(
            [
                sys.executable,
                "scripts/build_router.py",
                *_common_predecessor_args(fixture_root, predecessor_output),
            ],
            REPO_ROOT,
        )
        report = _installed_sdk_report(
            wheel,
            sdk_root,
            fixture_root,
            sdk_output,
            current_predecessor_ref,
            pin,
            root / "venv",
        )
        _verify_report(report, pin, current_predecessor_ref)

        predecessor_hashes = _artifact_hashes(
            predecessor_output,
            pin["artifact_names"],
        )
        sdk_hashes = _artifact_hashes(
            sdk_output,
            pin["artifact_names"],
            allowed_extra_entries={"routing-shadow-provenance.json"},
        )
        mismatches = [
            name
            for name in pin["artifact_names"]
            if (predecessor_output / name).read_bytes()
            != (sdk_output / name).read_bytes()
        ]
        if mismatches:
            raise RuntimeError(f"SDK release shadow byte mismatches: {mismatches}")
        expected_hashes = _read_json(expected_hashes_path)
        if (
            expected_hashes.get("predecessor_ref")
            != pin["predecessor"]["implementation_baseline_ref"]
        ):
            raise RuntimeError("SDK release expected-hash predecessor ref drifted")
        if expected_hashes.get("output_sha256") != predecessor_hashes:
            raise RuntimeError("canonical predecessor output hashes drifted")
        if sdk_hashes != predecessor_hashes:
            raise RuntimeError("SDK release shadow output hashes drifted")
        if report.get("artifact_sha256") != sdk_hashes:
            raise RuntimeError("installed SDK report hashes drifted from output bytes")

        result = {
            "abi_epoch": pin["abi_epoch"],
            "artifact_count": len(pin["artifact_names"]),
            "byte_parity": "14/14",
            "canonical_owner": "aoa-routing",
            "fixture_archive_sha256": pin["fixture"]["archive_sha256"],
            "local_release_wheel_sha256": _sha256(wheel),
            "predecessor_implementation_baseline_ref": pin["predecessor"][
                "implementation_baseline_ref"
            ],
            "predecessor_source_ref": current_predecessor_ref,
            "publication_posture": pin["publication_posture"],
            "sdk_release_ref": pin["sdk_release"]["source_ref"],
            "sdk_release_tag": pin["sdk_release"]["tag"],
            "sdk_release_tag_object_ref": pin["sdk_release"]["tag_object_ref"],
            "sdk_release_version": pin["sdk_release"]["version"],
        }
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
