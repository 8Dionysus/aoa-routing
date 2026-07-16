# AGENTS.md

This file applies to Python tooling under `scripts/`.

## Core split

`scripts/` is the routing seam of this repository:

- `build_router.py` writes the derived routing surfaces
- `router_core.py` holds shared constants, loaders, and derivation helpers
- `validate_router.py` enforces schema integrity, rebuild parity, and bounded cross-repo routing rules
- skill ingestion reads the owner agent catalog for callable bundles and the
  owner capability graph for typed navigation; it does not rebuild a local
  skill selector
- `validate_abyss_machine_routing_bundle.py` validates the OS Abyss ABI,
  SBOM-lite, SLSA/in-toto, and registry envelope for the generated routing
  readmodel family
- `validate_active_legacy_names.py` keeps old route names out of active path
  topology while allowing package-local legacy archives
- `validate_local_stats_port.py` delegates routing-local measurement and packet
  validation to the pinned `aoa-stats` contract owner
- `build_agon_gate_routing_registry.py` launches the active Agon part builder
- `validate_agon_gate_routing.py` launches the active Agon part validator
- `generate_decision_indexes.py` and `validate_decision_records.py` keep decision-rationale lookup surfaces derived and bounded

The controlling doctrine still applies here in full:

**Source repos own meaning. Routing repo owns navigation.**

## Editing posture

When changing script logic:

- keep routing deterministic and reviewable
- preserve the thin-router boundary
- prefer source-owned refs over copied summaries
- make missing-source or drift failures visible
- reuse `router_core.py` helpers instead of re-encoding routing rules ad hoc

Use extra care when touching:

- kind handling
- inspect and expand target derivation
- pairing logic
- federation-entry seams
- Agon gate-routing compatibility launchers; active logic lives under
  `mechanics/agon/parts/gate-routing/scripts/`
- task-to-tier dispatch logic
- rebuild parity expectations in `validate_router.py`

Do not hard-code upstream meaning into routing scripts.
If a change makes the router more semantic, more duplicative, or more authoritative, back up and tighten the boundary.

## Validation

After script changes, run the normal build and validation path:

```bash
python scripts/build_router.py
python scripts/validate_active_legacy_names.py
python scripts/validate_local_stats_port.py
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/validate_abyss_machine_routing_bundle.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python mechanics/agon/parts/gate-routing/scripts/build_agon_gate_routing_registry.py --check
python mechanics/agon/parts/gate-routing/scripts/validate_agon_gate_routing.py
python -m pytest -q tests
```

If only validator wiring changed, still run at least the validator and the relevant tests you touched.
