from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION_RELEASE_PREFIXES = (
    "certification_",
    "deployment_",
    "incident_",
    "release_gate_",
    "rollback_",
    "watchtower_",
)
CERTIFICATION_RELEASE_EXTRA_PAIRS = (
    (
        "mechanics/experience/parts/certification-owner-landing/schemas/certification_owner_route_v1.json",
        "mechanics/experience/parts/certification-owner-landing/examples/certification_owner_route.example.json",
    ),
    (
        "mechanics/recurrence/parts/incident-reentry/schemas/incident_reentry_route_v1.json",
        "mechanics/recurrence/parts/incident-reentry/examples/incident_reentry_route.example.json",
    ),
    (
        "mechanics/release-support/parts/deployment-ring-routing/schemas/deployment_route_signal_v1.json",
        "mechanics/release-support/parts/deployment-ring-routing/examples/deployment_route_signal.example.json",
    ),
    (
        "mechanics/release-support/parts/release-gate-routing/schemas/release_gate_route_decision_v1.json",
        "mechanics/release-support/parts/release-gate-routing/examples/release_gate_route_decision.example.json",
    ),
    (
        "mechanics/release-support/parts/watchtower-escalation/schemas/watchtower_escalation_route_v1.json",
        "mechanics/release-support/parts/watchtower-escalation/examples/watchtower_escalation_route.example.json",
    ),
)


def certification_release_pairs() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    seen_pairs: set[tuple[Path, Path]] = set()
    missing_pairs: list[str] = []
    for example_path in sorted((ROOT / "examples").glob("*.example.json")):
        stem = example_path.name.removesuffix(".example.json")
        if not stem.startswith(CERTIFICATION_RELEASE_PREFIXES):
            continue
        schema_candidates = [ROOT / "schemas" / f"{stem}_v1.json"]
        if stem.endswith("_v1"):
            schema_candidates.insert(0, ROOT / "schemas" / f"{stem}.json")
        schema_path = next((candidate for candidate in schema_candidates if candidate.exists()), None)
        if schema_path is None:
            expected_schema = schema_candidates[0]
            missing_pairs.append(f"{example_path.relative_to(ROOT)} -> {expected_schema.relative_to(ROOT)}")
            continue
        pair = (schema_path, example_path)
        if pair not in seen_pairs:
            pairs.append(pair)
            seen_pairs.add(pair)

    for schema_path in sorted((ROOT / "schemas").glob("*_v1.json")):
        legacy_stem = schema_path.name.removesuffix("_v1.json")
        schema_stem = schema_path.name.removesuffix(".json")
        if not (legacy_stem.startswith(CERTIFICATION_RELEASE_PREFIXES) or schema_stem.startswith(CERTIFICATION_RELEASE_PREFIXES)):
            continue
        example_candidates = [
            ROOT / "examples" / f"{legacy_stem}.example.json",
            ROOT / "examples" / f"{schema_stem}.example.json",
        ]
        example_path = next((candidate for candidate in example_candidates if candidate.exists()), None)
        if example_path is None:
            missing_pairs.append(
                f"{schema_path.relative_to(ROOT)} -> {example_candidates[0].relative_to(ROOT)}"
            )
            continue
        pair = (schema_path, example_path)
        if pair not in seen_pairs:
            pairs.append(pair)
            seen_pairs.add(pair)

    for schema_ref, example_ref in CERTIFICATION_RELEASE_EXTRA_PAIRS:
        schema_path = ROOT / schema_ref
        example_path = ROOT / example_ref
        if not schema_path.exists():
            missing_pairs.append(f"{example_path.relative_to(ROOT)} -> {schema_path.relative_to(ROOT)}")
        if not example_path.exists():
            missing_pairs.append(f"{schema_path.relative_to(ROOT)} -> {example_path.relative_to(ROOT)}")
        pair = (schema_path, example_path)
        if schema_path.exists() and example_path.exists() and pair not in seen_pairs:
            pairs.append(pair)
            seen_pairs.add(pair)

    assert not missing_pairs, "missing certification/release contract pair(s): " + ", ".join(missing_pairs)
    return pairs


def test_certification_release_examples_match_schemas() -> None:
    pairs = certification_release_pairs()
    assert pairs
    for schema_path, example_path in pairs:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        example = json.loads(example_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda error: list(error.path))
        assert not errors, f"{example_path.name}: {errors[0].message if errors else ''}"
