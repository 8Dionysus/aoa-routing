from __future__ import annotations

import importlib.util
import io
import json
import sys
import tarfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
PART_ROOT = (
    REPO_ROOT
    / "mechanics"
    / "release-support"
    / "parts"
    / "release-gate-routing"
)
VERIFIER_PATH = PART_ROOT / "scripts" / "verify_sdk_shadow_release_parity.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_sdk_shadow_release_parity",
        VERIFIER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sdk_shadow_release_pin_is_strict_and_non_authorizing() -> None:
    verifier = _load_verifier()
    pin = verifier.load_pin()

    assert pin["state"] == "predecessor_canonical"
    assert pin["publication_posture"] == "sdk_shadow_non_publishing"
    assert pin["predecessor"]["canonical_owner"] == "aoa-routing"
    assert pin["predecessor"]["implementation_baseline_ref"] == (
        "7e2fe467ad26aa645b61849001a456dda4562ffc"
    )
    assert pin["sdk_release"]["tag"] == "v0.6.0"
    assert pin["sdk_release"]["tag_object_ref"] == (
        "14e34a7eb5515dbb788c7fa1373dbcaf43d51163"
    )
    assert pin["sdk_release"]["source_ref"] == (
        "f3e23b60ec483ce81f5abe9aafe7303c15df2102"
    )
    assert len(pin["artifact_names"]) == 14
    assert not any(pin["gates"].values())


def test_sdk_shadow_release_pin_schema_rejects_authority_escalation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verifier = _load_verifier()
    pin = json.loads(verifier.PIN_PATH.read_text(encoding="utf-8"))
    pin["gates"]["g5_owner_switch"] = True
    invalid_pin = tmp_path / "invalid-pin.json"
    invalid_pin.write_text(json.dumps(pin), encoding="utf-8")
    monkeypatch.setattr(verifier, "PIN_PATH", invalid_pin)

    with pytest.raises(RuntimeError, match="invalid SDK shadow release pin"):
        verifier.load_pin()


@pytest.mark.parametrize(
    ("member_name", "member_kind", "message"),
    [
        ("../escape.json", "file", "unsafe fixture archive path"),
        ("linked.json", "symlink", "unsupported fixture archive member"),
    ],
)
def test_sdk_shadow_fixture_materializer_rejects_unsafe_members(
    tmp_path: Path,
    member_name: str,
    member_kind: str,
    message: str,
) -> None:
    verifier = _load_verifier()
    archive_path = tmp_path / "unsafe.tar.gz"
    with tarfile.open(archive_path, mode="w:gz") as archive:
        member = tarfile.TarInfo(member_name)
        if member_kind == "symlink":
            member.type = tarfile.SYMTYPE
            member.linkname = "target.json"
            archive.addfile(member)
        else:
            payload = b"{}\n"
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))

    with pytest.raises(RuntimeError, match=message):
        verifier.safe_materialize_fixture(archive_path, tmp_path / "fixture")


def test_sdk_shadow_fixture_materializer_rejects_duplicate_paths(
    tmp_path: Path,
) -> None:
    verifier = _load_verifier()
    archive_path = tmp_path / "duplicate.tar.gz"
    with tarfile.open(archive_path, mode="w:gz") as archive:
        for payload in (b"first\n", b"second\n"):
            member = tarfile.TarInfo("duplicate.txt")
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))

    with pytest.raises(RuntimeError, match="duplicate fixture archive path"):
        verifier.safe_materialize_fixture(archive_path, tmp_path / "fixture")


def test_repo_validation_pins_the_same_sdk_release() -> None:
    pin = json.loads(
        (PART_ROOT / "config" / "sdk_shadow_release_pin.json").read_text(
            encoding="utf-8"
        )
    )
    workflow = (REPO_ROOT / ".github" / "workflows" / "repo-validation.yml").read_text(
        encoding="utf-8"
    )
    release_check = (REPO_ROOT / "scripts" / "release_check.py").read_text(
        encoding="utf-8"
    )

    assert f"ref: {pin['sdk_release']['source_ref']}" in workflow
    assert "AOA_SDK_SHADOW_RELEASE_ROOT: ./aoa-sdk" in workflow
    assert "verify_sdk_shadow_release_parity.py" in release_check
