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


def test_thin_router_bundle_covers_live_generated_route_family() -> None:
    manifest = json.loads((REPO_ROOT / "docs" / "artifact-bundles" / "thin_router.bundle.json").read_text())
    subjects = {entry["path"] for entry in manifest["artifact_subjects"]}
    expected_generated_subjects = {
        "generated/aoa_router.min.json",
        "generated/composite_stress_route_hints.min.json",
        "generated/cross_repo_registry.min.json",
        "generated/federation_entrypoints.min.json",
        "generated/kag_source_lift_relation_hints.min.json",
        "generated/owner_layer_shortlist.min.json",
        "generated/pairing_hints.min.json",
        "generated/quest_dispatch_hints.min.json",
        "generated/recommended_paths.min.json",
        "generated/return_navigation_hints.min.json",
        "generated/stats_regrounding_hints.min.json",
        "generated/task_to_surface_hints.json",
        "generated/task_to_tier_hints.json",
        "generated/tiny_model_entrypoints.json",
    }
    retired_subjects = {path for path in subjects if "two_stage" in path or "two-stage" in path}

    assert expected_generated_subjects - subjects == set()
    assert retired_subjects == set()
    assert {
        path for path in expected_generated_subjects if not (REPO_ROOT / path).exists()
    } == set()


def test_federation_entry_abi_uses_current_kag_mechanics_paths() -> None:
    abi = (
        REPO_ROOT
        / "mechanics"
        / "boundary-bridge"
        / "parts"
        / "federation-entry"
        / "docs"
        / "federation-entry-abi.md"
    ).read_text()

    assert "aoa-kag/generated/federation_spine.min.json" not in abi
    assert "aoa-kag/generated/tos_zarathustra_route_retrieval_pack.min.json" not in abi
    assert (
        "aoa-kag/mechanics/boundary-bridge/parts/federation-spine/generated/federation_spine.min.json"
        in abi
    )
    assert (
        "aoa-kag/mechanics/boundary-bridge/parts/tos-retrieval-axis/generated/"
        "tos_zarathustra_route_retrieval_pack.min.json"
        in abi
    )


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
    assert state["unexpected_pre_materialization_blockers"] == []


def test_thin_router_bundle_validator_rejects_extra_pre_materialization_blocker() -> None:
    validator = load_bundle_validator()
    state = validator._trust_gate_pre_materialization_state(
        artifact_bundles=type(
            "FakeArtifactBundles",
            (),
            {
                "trust_gate": staticmethod(
                    lambda *_args, **_kwargs: {
                        "verdict": "deny",
                        "blockers": ["unexpected_trust_regression"],
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

    assert state["ok"] is False
    assert state["expected_pre_materialization_deny"] is False
    assert state["unexpected_pre_materialization_blockers"] == ["unexpected_trust_regression"]


def test_thin_router_bundle_validator_rejects_pre_materialization_allow() -> None:
    validator = load_bundle_validator()
    state = validator._trust_gate_pre_materialization_state(
        artifact_bundles=type(
            "FakeArtifactBundles",
            (),
            {
                "trust_gate": staticmethod(
                    lambda *_args, **_kwargs: {
                        "ok": True,
                        "verdict": "allow",
                        "decision": {
                            "allow": True,
                            "model": "fail_closed_consumer_admission",
                            "blockers": [],
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

    assert state["ok"] is False
    assert state["mode"] == "unexpected_pre_materialization_state"
    assert state["expected_pre_materialization_deny"] is False
