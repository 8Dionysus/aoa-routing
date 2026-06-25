from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


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
