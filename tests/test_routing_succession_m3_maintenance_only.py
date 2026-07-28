from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
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
VERIFIER_PATH = (
    PART_ROOT / "scripts" / "validate_routing_maintenance_only.py"
)


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "validate_routing_maintenance_only",
        VERIFIER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_m3_receipt_is_strict_and_keeps_archive_forbidden() -> None:
    verifier = _load_verifier()
    result = verifier.validate()

    assert result["status"] == "maintenance_only"
    assert result["canonical_producer"] == "aoa-sdk"
    assert result["workflow_contours"] == 1
    assert result["sibling_checkouts"] == 0
    assert result["producer_generation_in_ci"] is False
    assert (
        result["maintenance_base_ref"]
        == "97f60de1b5992ef6bf5ff0f051bd452d940d9a85"
    )
    assert result["changed_path_count"] > 0
    assert result["approved_retained_source_paths"] == []
    assert result["consumer_zero"] is False
    assert result["archive_ready"] is False
    assert result["archive_authorized"] is False


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("gates", "consumer_zero", True),
        ("gates", "archive_ready", True),
        ("gates", "archive_authorized", True),
        ("compatibility_window", "rollback_retired", True),
    ],
)
def test_m3_schema_rejects_premature_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    section: str,
    field: str,
    value: object,
) -> None:
    verifier = _load_verifier()
    evidence = json.loads(verifier.EVIDENCE_PATH.read_text(encoding="utf-8"))
    evidence[section][field] = value
    invalid = tmp_path / "invalid-m3-evidence.json"
    invalid.write_text(json.dumps(evidence), encoding="utf-8")
    monkeypatch.setattr(verifier, "EVIDENCE_PATH", invalid)

    with pytest.raises(RuntimeError, match="invalid M3 maintenance-only evidence"):
        verifier.load_evidence()


def test_active_gate_has_no_sibling_or_producer_contour() -> None:
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "repo-validation.yml"
    ).read_text(encoding="utf-8")
    release_check = (REPO_ROOT / "scripts" / "release_check.py").read_text(
        encoding="utf-8"
    )

    assert "repository: 8Dionysus/" not in workflow
    assert "build_router.py" not in workflow
    assert "validate_router.py" not in workflow
    assert "--base-ref" not in workflow
    assert "AOA_SDK" not in release_check
    assert "build_router" not in release_check
    assert "validate_router" not in release_check


def test_m3_diff_guard_includes_deleted_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verifier = _load_verifier()
    captured_args: tuple[str, ...] = ()

    def fake_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        nonlocal captured_args
        captured_args = args
        return subprocess.CompletedProcess(
            args=["git", *args],
            returncode=0,
            stdout="D\tgenerated/aoa_router.min.json\n",
            stderr="",
        )

    monkeypatch.setattr(verifier, "_git", fake_git)

    assert verifier._changed_paths("base-ref") == (
        "generated/aoa_router.min.json",
    )
    assert "--name-status" in captured_args
    assert "--diff-filter=ACDMRTUXB" in captured_args


def test_m3_workflow_inventory_includes_yml_and_yaml(tmp_path: Path) -> None:
    verifier = _load_verifier()
    workflow_root = tmp_path / ".github" / "workflows"
    workflow_root.mkdir(parents=True)
    (workflow_root / "repo-validation.yml").write_text(
        "name: Repo Validation\n",
        encoding="utf-8",
    )
    (workflow_root / "producer.yaml").write_text(
        "name: Producer\n",
        encoding="utf-8",
    )

    assert tuple(path.name for path in verifier._workflow_paths(workflow_root)) == (
        "producer.yaml",
        "repo-validation.yml",
    )


def _approval(
    *,
    path: str,
    blob_id: str,
) -> dict[str, object]:
    return {
        "schema_version": "aoa_routing_maintenance_approval_v1",
        "approval_id": "AOA-RT-MA-0001",
        "change_class": "compatibility",
        "approved_on": "2026-07-28",
        "approval": {
            "status": "approved",
            "approved_by": "routing-owner",
            "approval_ref": "https://github.com/8Dionysus/aoa-routing/pull/999",
        },
        "scope": {
            "maintenance_base_ref": (
                "97f60de1b5992ef6bf5ff0f051bd452d940d9a85"
            ),
            "retained_source_blobs": [
                {
                    "path": path,
                    "git_blob_id": blob_id,
                }
            ],
        },
        "claim_limit": (
            "This packet approves only the exact retained-source blob and "
            "does not reopen producer or publication authority."
        ),
    }


@pytest.mark.parametrize(
    ("path", "requires_approval"),
    [
        ("routing/core/router.py", True),
        ("routing/source_home.manifest.json", True),
        ("scripts/build_router.py", True),
        ("mechanics/agon/parts/gate-routing/config/gate.json", True),
        ("routing/AGENTS.md", False),
        ("routing/README.md", False),
        ("docs/security-notice.md", False),
        ("tests/fixtures/generated/router.json", False),
    ],
)
def test_m3_diff_guard_separates_retained_source_from_docs_and_tests(
    path: str,
    requires_approval: bool,
) -> None:
    verifier = _load_verifier()

    assert verifier._is_retained_implementation_path(path) is requires_approval


def test_m3_rejects_new_producer_or_publication_entrypoint() -> None:
    verifier = _load_verifier()
    evidence = verifier.load_evidence()
    entry = verifier.ChangedPath(status="A", path="scripts/publish_router.py")

    with pytest.raises(
        RuntimeError,
        match="new, structural, or generated predecessor implementation",
    ):
        verifier._validate_change_boundary(
            (entry,),
            (),
            evidence=evidence,
            base_ref=evidence["pins"]["predecessor"]["maintenance_base_ref"],
        )


def test_m3_rejects_unapproved_retained_source_modification() -> None:
    verifier = _load_verifier()
    evidence = verifier.load_evidence()
    entry = verifier.ChangedPath(status="M", path="routing/core/router.py")

    with pytest.raises(RuntimeError, match="exact reviewed maintenance approval"):
        verifier._validate_change_boundary(
            (entry,),
            (),
            evidence=evidence,
            base_ref=evidence["pins"]["predecessor"]["maintenance_base_ref"],
            blob_resolver=lambda path: "a" * 40,
        )


def test_m3_accepts_exact_approved_retained_source_blob() -> None:
    verifier = _load_verifier()
    evidence = verifier.load_evidence()
    path = "routing/core/router.py"
    blob_id = "a" * 40
    entry = verifier.ChangedPath(status="M", path=path)
    approval = _approval(path=path, blob_id=blob_id)

    assert verifier._validate_change_boundary(
        (entry,),
        (approval,),
        evidence=evidence,
        base_ref=evidence["pins"]["predecessor"]["maintenance_base_ref"],
        blob_resolver=lambda candidate: blob_id,
    ) == (path,)


def test_m3_rejects_generated_output_even_with_approval() -> None:
    verifier = _load_verifier()
    evidence = verifier.load_evidence()
    path = "generated/aoa_router.min.json"
    blob_id = "b" * 40
    entry = verifier.ChangedPath(status="M", path=path)
    approval = _approval(path=path, blob_id=blob_id)

    with pytest.raises(
        RuntimeError,
        match="approval cannot cover generated",
    ):
        verifier._validate_change_boundary(
            (entry,),
            (approval,),
            evidence=evidence,
            base_ref=evidence["pins"]["predecessor"]["maintenance_base_ref"],
            blob_resolver=lambda candidate: blob_id,
        )


def test_m3_rejects_approval_bound_to_another_base() -> None:
    verifier = _load_verifier()
    evidence = verifier.load_evidence()
    approval = _approval(
        path="routing/core/router.py",
        blob_id="c" * 40,
    )
    approval["scope"]["maintenance_base_ref"] = "d" * 40

    with pytest.raises(RuntimeError, match="wrong maintenance base"):
        verifier._validate_change_boundary(
            (),
            (approval,),
            evidence=evidence,
            base_ref=evidence["pins"]["predecessor"]["maintenance_base_ref"],
        )


def test_m3_loads_schema_valid_approval_packet(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verifier = _load_verifier()
    approval_root = tmp_path / "maintenance-approvals"
    approval_root.mkdir()
    approval = _approval(
        path="routing/core/router.py",
        blob_id="e" * 40,
    )
    (approval_root / "AOA-RT-MA-0001.json").write_text(
        json.dumps(approval),
        encoding="utf-8",
    )
    monkeypatch.setattr(verifier, "APPROVAL_ROOT", approval_root)

    assert verifier.load_approvals() == (approval,)
