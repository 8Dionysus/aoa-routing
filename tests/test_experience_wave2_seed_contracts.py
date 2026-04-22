from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
WAVE2_PREFIXES = (
    "certification_",
    "deployment_",
    "incident_",
    "release_gate_",
    "rollback_",
    "watchtower_",
)


def wave2_pairs() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    seen_pairs: set[tuple[Path, Path]] = set()
    missing_pairs: list[str] = []
    for example_path in sorted((ROOT / "examples").glob("*.example.json")):
        stem = example_path.name.removesuffix(".example.json")
        if not stem.startswith(WAVE2_PREFIXES):
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
        if not (legacy_stem.startswith(WAVE2_PREFIXES) or schema_stem.startswith(WAVE2_PREFIXES)):
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

    assert not missing_pairs, "missing wave2 contract pair(s): " + ", ".join(missing_pairs)
    return pairs


def test_experience_wave2_examples_match_schemas() -> None:
    pairs = wave2_pairs()
    assert pairs
    for schema_path, example_path in pairs:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        example = json.loads(example_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda error: list(error.path))
        assert not errors, f"{example_path.name}: {errors[0].message if errors else ''}"
