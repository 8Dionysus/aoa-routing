from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_thin_router_bundle_declares_consumer_trust_path() -> None:
    manifest = json.loads((REPO_ROOT / "docs" / "artifact-bundles" / "thin_router.bundle.json").read_text())

    commands = manifest["consumer_command"]
    joined = "\n".join(commands)

    assert "bundle-register" in joined
    assert "materialize-subjects" in joined
    assert "trust-gate" in joined
    assert "registry-latest" in joined
    assert "--expected-source-repo aoa-routing" in joined
    assert "--source-repo aoa-routing" in joined
