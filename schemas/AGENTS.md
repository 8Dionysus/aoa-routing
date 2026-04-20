# AGENTS.md

This file applies to schema contracts under `schemas/`.

## What lives here

`schemas/` defines the public contract surfaces for the router's derived outputs.
These files describe envelope shape, router entries, hint objects, and bounded hop surfaces.

Key schemas here include:

- `aoa-router.schema.json`
- `cross-repo-registry.schema.json`
- `router-entry.schema.json`
- `task-to-surface-hints.schema.json`
- `task-to-tier-hints.schema.json`
- `quest_dispatch_hint.schema.json`
- `quest-dispatch-hints.schema.json`
- `recommended-paths.schema.json`
- `pairing-hints.schema.json`
- `kag-source-lift-relation-hints.schema.json`
- `federation-entrypoints.schema.json`
- `agon-gate-routing-registry.schema.json`
- `agon-gate-trigger.schema.json`
- `agon-gate-route-hint.schema.json`
- `tiny-model-entrypoints.schema.json`

## Editing posture

A schema change is a contract change.
Treat it as a public interface decision, not a cosmetic cleanup.

When editing schema files:

- keep bounded routing posture explicit
- preserve repo-relative refs and typed action shapes
- do not loosen the contract until the builder, validator, and tests all agree
- do not permit copied source-owned meaning to sneak into routing payloads
- update related logic in `scripts/build_router.py` and `scripts/validate_router.py` when shape changes are intentional

Prefer backward-compatible tightening when possible.
If a breaking change is necessary, call it out explicitly in the final report.

## Validation

After schema edits, run:

```bash
python scripts/build_agon_gate_routing_registry.py --check
python scripts/validate_agon_gate_routing.py
python scripts/validate_router.py
pytest tests
```

If the schema change affects generated output shape, rebuild before validating.
