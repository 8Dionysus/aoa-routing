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
            stdout="generated/aoa_router.min.json\n",
            stderr="",
        )

    monkeypatch.setattr(verifier, "_git", fake_git)

    assert verifier._changed_paths("base-ref") == (
        "generated/aoa_router.min.json",
    )
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


@pytest.mark.parametrize(
    ("path", "is_producer"),
    [
        ("routing/core/README.md", True),
        ("routing/source_home.manifest.json", True),
        ("generated/aoa_router.min.json", True),
        ("scripts/build_router.py", True),
        ("routing/AGENTS.md", False),
        ("routing/README.md", False),
        ("docs/security-notice.md", False),
    ],
)
def test_m3_diff_guard_separates_producer_from_maintenance_docs(
    path: str,
    is_producer: bool,
) -> None:
    verifier = _load_verifier()

    assert verifier._is_producer_path(path) is is_producer
