# Release Support Provenance

## Former Flat Paths

- `docs/RELEASE_GATE_ROUTING.md`
- `docs/RELEASING.md`
- `docs/DEPLOYMENT_RING_ROUTING.md`
- `docs/INSTALLATION_BOUNDARY_ROUTING.md`
- `docs/INSTALLATION_ROUTE_PLAN.md`
- `docs/WATCHTOWER_ESCALATION_ROUTING.md`
- `schemas/release_gate_route_decision_v1.json`
- `schemas/deployment_route_signal_v1.json`
- `schemas/installation_route_plan_v1.json`
- `schemas/watchtower_escalation_route_v1.json`
- matching examples

## Current Active Parts

- `parts/release-gate-routing/`
- `parts/deployment-ring-routing/`
- `parts/installation-routing/`
- `parts/watchtower-escalation/`

## Legacy Boundary

Former flat paths are recorded in `legacy/`. Active tests and validators must
read from part paths, not from legacy.
