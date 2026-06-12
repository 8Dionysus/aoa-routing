# Antifragility Provenance

## Former Flat Paths

- `docs/STRESS_POSTURE_ROUTING.md`
- `docs/ROUTING_STRESS_CHAOS.md`
- `docs/DEGRADED_ROUTE_HINTS.md`
- `docs/PLAYBOOK_STRESS_ROUTE_CONSUMPTION.md`
- `docs/KAG_QUARANTINE_ROUTE_HINTS.md`
- `docs/ROLLBACK_ROUTE_SIGNALS.md`
- `docs/AUTO_ROLLBACK_DISPATCH.md`
- `docs/STAY_ORDER_DISPATCH.md`
- `docs/VIA_NEGATIVA_CHECKLIST.md`
- `schemas/stress_navigation_hint_v1.json`
- `schemas/composite_stress_route_hint_v1.json`
- `schemas/composite-stress-route-hints.schema.json`
- `schemas/rollback_route_signal_v1.json`
- `schemas/rollback_dispatch_v1.json`
- `examples/stress_navigation_hint*.json`
- `examples/composite_stress_route_hint*.json`
- `examples/rollback_route_signal_v1.example.json`
- `examples/rollback_dispatch.example.json`

## Current Active Parts

- `parts/stress-routing/`
- `parts/degraded-route-hints/`
- `parts/composite-stress-routing/`
- `parts/quarantine-routing/`
- `parts/rollback-routing/`
- `parts/via-negativa/`

Root `generated/composite_stress_route_hints.min.json` remains a public routing
read model. Its contract schema is active in `parts/composite-stress-routing/`.

## Legacy Boundary

Former flat paths are recorded in `legacy/`. Active tests and validators must
read from the part paths, not from legacy.
