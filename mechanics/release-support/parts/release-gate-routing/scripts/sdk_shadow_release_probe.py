#!/usr/bin/env python3
"""Exercise the installed aoa-sdk routing shadow producer."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and validate an SDK shadow bundle from an installed wheel."
    )
    parser.add_argument("--fixture-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pin", type=Path, required=True)
    parser.add_argument("--sdk-checkout", type=Path, required=True)
    parser.add_argument("--predecessor-source-ref", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pin = json.loads(args.pin.read_text(encoding="utf-8"))

    from aoa_sdk.control_plane.routing.shadow import (
        RoutingProducerInputs,
        build_shadow_bundle,
        validate_shadow_bundle,
    )
    from aoa_sdk.control_plane.routing.validator import SCHEMA_ROOT

    import aoa_sdk.control_plane.routing.shadow as shadow_module

    module_path = Path(shadow_module.__file__).resolve()
    sdk_checkout = args.sdk_checkout.resolve()
    if sdk_checkout == module_path or sdk_checkout in module_path.parents:
        raise SystemExit(f"probe imported SDK routing source from checkout: {module_path}")
    environment_root = Path(sys.prefix).resolve()
    if environment_root not in module_path.parents:
        raise SystemExit(
            "installed SDK routing module is outside the probe environment: "
            f"{module_path}"
        )

    fixture_root = args.fixture_root.resolve()
    inputs = RoutingProducerInputs(
        techniques_root=fixture_root / "aoa-techniques",
        skills_root=fixture_root / "aoa-skills",
        evals_root=fixture_root / "aoa-evals",
        memo_root=fixture_root / "aoa-memo",
        stats_root=fixture_root / "aoa-stats",
        agents_root=fixture_root / "aoa-agents",
        aoa_root=fixture_root / "Agents-of-Abyss",
        playbooks_root=fixture_root / "aoa-playbooks",
        kag_root=fixture_root / "aoa-kag",
        tos_root=fixture_root / "Tree-of-Sophia",
        sdk_root=fixture_root / "aoa-sdk",
        source_route_root=fixture_root / "Dionysus",
        profile_root=fixture_root / "8Dionysus",
        abyss_stack_root=fixture_root / "abyss-stack",
    )
    bundle = build_shadow_bundle(
        inputs,
        args.output_dir.resolve(),
        predecessor_source_ref=args.predecessor_source_ref,
        sdk_source_ref=pin["sdk_release"]["source_ref"],
        input_source_refs=pin["fixture"]["input_source_refs"],
        observed_at=datetime.now(timezone.utc),
    )
    validate_shadow_bundle(bundle, inputs)

    provenance = json.loads(bundle.provenance_path.read_text(encoding="utf-8"))
    packaged_schemas = sorted(SCHEMA_ROOT.glob("*.json"))
    report = {
        "abi_epoch": provenance["abi_epoch"],
        "artifact_count": len(bundle.artifact_sha256),
        "artifact_sha256": dict(sorted(bundle.artifact_sha256.items())),
        "canonical_producer": provenance["canonical_producer"],
        "input_source_refs": provenance["input_source_refs"],
        "module_path": str(module_path),
        "package_version": version("aoa-sdk"),
        "publication_posture": provenance["publication_posture"],
        "schema_count": len(packaged_schemas),
        "shadow_producer": provenance["shadow_producer"],
        "sidecar": bundle.provenance_path.name,
        "state": provenance["state"],
    }
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
