# Release Gate Routing

Owns release gate route decisions and the repo release runbook.

Current payloads:

- `evidence/routing-succession-m3-maintenance-only.json`
- `docs/release-gate-routing.md`
- `docs/routing-succession-m3-maintenance-only.md`
- `docs/releasing.md`
- `schemas/routing-succession-m3-maintenance-only.schema.json`
- `schemas/release_gate_route_decision_v1.json`
- `examples/release_gate_route_decision.example.json`
- `scripts/validate_routing_maintenance_only.py`

Historical M1 and M2 transition evidence remains immutable under `config/`,
`docs/`, `evidence/`, `schemas/`, and `scripts/`. It is no longer part of the
active release or CI route.
- `scripts/verify_sdk_shadow_release_parity.py`
