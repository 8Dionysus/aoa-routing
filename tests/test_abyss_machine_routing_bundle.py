from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_bundle_validator():
    script = REPO_ROOT / "scripts" / "validate_abyss_machine_routing_bundle.py"
    spec = importlib.util.spec_from_file_location("aoa_routing_bundle_validator", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_thin_router_bundle_declares_consumer_trust_path() -> None:
    manifest = json.loads((REPO_ROOT / "docs" / "artifact-bundles" / "thin_router.bundle.json").read_text())

    commands = manifest["consumer_command"]
    joined = "\n".join(commands)

    assert "evidence-promote" in joined
    assert "materialize-subjects" in joined
    assert "trust-gate" in joined
    assert "registry-latest" in joined
    assert "--consumer-ref aoa-routing:thin-router-readmodel" in joined
    assert "--source-repo aoa-routing" in joined
    assert "--trust-root-mode host_managed" in joined
    assert manifest["consumer_contract"]["subject_store_required"] is True
    assert manifest["consumer_contract"]["admission_gate"] == "fail_closed_consumer_admission"


def test_thin_router_bundle_validator_accepts_expected_pre_materialization_deny() -> None:
    validator = load_bundle_validator()
    state = validator._trust_gate_pre_materialization_state(
        artifact_bundles=type(
            "FakeArtifactBundles",
            (),
            {
                "trust_gate": staticmethod(
                    lambda *_args, **_kwargs: {
                        "verdict": "deny",
                        "decision": {
                            "allow": False,
                            "model": "fail_closed_consumer_admission",
                            "blockers": [validator.REQUIRED_SUBJECT_STORE_BLOCKER],
                        },
                        "inspected_claims": {
                            "registry_latest": {"selected_record_is_latest": True},
                            "controls": {"required_controls_missing": []},
                            "source": {"source_repo_matched": True},
                            "trust_root": {"trust_root_mode_matched": True},
                            "artifact_subject_store": {"required": True, "ok": False},
                        },
                    }
                )
            },
        )(),
        registry_dir=REPO_ROOT / "dist" / "test-registry",
        registry={"promoted": {"record": {"subject_digest": "sha256:" + ("1" * 64)}}},
    )

    assert state["ok"] is True
    assert state["mode"] == "deny_until_subject_store_materialized"
    assert state["expected_pre_materialization_deny"] is True
