# Recurrence Provenance

## Former Flat Paths

- `docs/RECURRENCE_NAVIGATION_BOUNDARY.md`
- `docs/RECURRENCE_DOWNSTREAM_HINTS.md`
- `docs/INCIDENT_REENTRY_ROUTING.md`
- `schemas/return-navigation-hints.schema.json`
- `schemas/recurrence-routing-projection.schema.json`
- `schemas/incident_reentry_route_v1.json`
- `examples/recurrence_routing_projection.example.json`
- `examples/incident_reentry_route.example.json`

## Current Active Parts

- `parts/return-navigation/`
- `parts/downstream-hints/`
- `parts/incident-reentry/`

Root `generated/return_navigation_hints.min.json` remains a public routing read
model. Its contract schema is active in `parts/return-navigation/`.

## Legacy Boundary

Former flat paths are recorded in `legacy/`. Active tests and validators must
read from part paths, not from legacy.
