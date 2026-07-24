from __future__ import annotations

import importlib.util
import json
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
VERIFIER_PATH = PART_ROOT / "scripts" / "verify_routing_succession_m2_handoff.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_routing_succession_m2_handoff",
        VERIFIER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_m2_handoff_is_strict_and_does_not_switch_owners() -> None:
    verifier = _load_verifier()
    evidence = verifier.load_evidence()

    assert evidence["status"] == "conditional_handoff_ready"
    assert evidence["scope"]["current_state"] == "predecessor_canonical"
    assert evidence["scope"]["canonical_producer"] == "aoa-routing"
    assert evidence["feature_acceptance"]["before_g5"] == "owner_normal_until_g5"
    assert evidence["compatibility_window"]["state"] == "not_started"
    assert evidence["compatibility_window"]["started_on"] is None
    assert evidence["gates"]["sdk_g4_admitted"]
    assert evidence["gates"]["conditional_handoff_ready"]
    assert not any(
        evidence["gates"][field]
        for field in (
            "g5_owner_switch",
            "predecessor_maintenance_only",
            "sdk_canonical",
            "live_runtime_sdk_provenance_verified",
            "compatibility_window_started",
            "consumer_zero",
            "rollback_retired",
            "archive_ready",
            "archive_authorized",
        )
    )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("gates", "g5_owner_switch"), True),
        (("gates", "predecessor_maintenance_only"), True),
        (("feature_acceptance", "before_g5"), "maintenance_only"),
        (("compatibility_window", "state"), "active"),
    ],
)
def test_m2_schema_rejects_premature_transition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    path: tuple[str, str],
    value: object,
) -> None:
    verifier = _load_verifier()
    evidence = json.loads(verifier.EVIDENCE_PATH.read_text(encoding="utf-8"))
    evidence[path[0]][path[1]] = value
    invalid = tmp_path / "invalid-m2-evidence.json"
    invalid.write_text(json.dumps(evidence), encoding="utf-8")
    monkeypatch.setattr(verifier, "EVIDENCE_PATH", invalid)

    with pytest.raises(RuntimeError, match="invalid M2 conditional handoff evidence"):
        verifier.load_evidence()


def test_release_gate_pins_separate_release_and_g4_checkouts() -> None:
    evidence = json.loads(
        (
            PART_ROOT
            / "evidence"
            / "routing-succession-m2-conditional-handoff.json"
        ).read_text(encoding="utf-8")
    )
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "repo-validation.yml"
    ).read_text(encoding="utf-8")
    release_check = (REPO_ROOT / "scripts" / "release_check.py").read_text(
        encoding="utf-8"
    )

    assert f"ref: {evidence['pins']['sdk_g4']['merge_ref']}" in workflow
    assert "path: .deps/aoa-sdk-g4" in workflow
    assert "AOA_SDK_G4_ROOT: ./.deps/aoa-sdk-g4" in workflow
    assert "verify_routing_succession_m2_handoff.py" in release_check
