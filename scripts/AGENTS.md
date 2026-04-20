# AGENTS.md

This file applies to Python tooling under `scripts/`.

## Core split

`scripts/` is the routing seam of this repository:

- `build_router.py` writes the derived routing surfaces
- `router_core.py` holds shared constants, loaders, and derivation helpers
- `validate_router.py` enforces schema integrity, rebuild parity, and bounded cross-repo routing rules
- `build_agon_gate_routing_registry.py` writes the additive Wave V gate-routing surface
- `validate_agon_gate_routing.py` enforces the pre-protocol gate-routing stop-lines

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
- Agon gate-routing stop-lines and decision states
- task-to-tier dispatch logic
- rebuild parity expectations in `validate_router.py`

Do not hard-code upstream meaning into routing scripts.
If a change makes the router more semantic, more duplicative, or more authoritative, back up and tighten the boundary.

## Validation

After script changes, run the normal build and validation path:

```bash
python scripts/build_router.py
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/build_agon_gate_routing_registry.py --check
python scripts/validate_agon_gate_routing.py
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python -m pytest -q tests
```

If only validator wiring changed, still run at least the validator and the relevant tests you touched.
