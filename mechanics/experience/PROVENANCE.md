# Experience Provenance

## Former Flat Paths

- `docs/FIRST_OFFICE_ROUTE_GATE.md`
- `docs/OFFICE_ROUTE_GATE.md`
- `docs/OFFICE_HANDOFF_PACKET.md`
- `docs/SERVICE_HANDOFF_GRAPH.md`
- `docs/SERVICE_TO_AGON_BOUNDARY.md`
- `docs/ADOPTION_ESCALATION_PATHS.md`
- `docs/ADOPTION_OWNER_QUEST_FANOUT.md`
- `docs/ADOPTION_REENTRY_ROUTING.md`
- `docs/ADOPTION_ROUTING_GATE.md`
- `docs/ADOPTION_SUPPRESSION_ROUTING.md`
- `docs/ROUTE_RULE_ADOPTION.md`
- `docs/CERTIFICATION_OWNER_LANDING.md`
- `schemas/first_office_route_gate_v1.json`
- `schemas/office_route_gate_v1.json`
- `schemas/office_handoff_packet_v1.json`
- `schemas/service_handoff_graph_v1.json`
- `schemas/service_escalation_signal_v1.json`
- `schemas/service_to_agon_boundary_signal_v1.json`
- `schemas/adoption_*.json`
- `schemas/route_rule_adoption_*.json`
- `schemas/certification_owner_route_v1.json`
- matching `examples/*.example.json`

## Current Active Parts

- `parts/office-route-gate/`
- `parts/service-handoff/`
- `parts/adoption-routing/`
- `parts/certification-owner-landing/`

## Legacy Boundary

Former flat paths are recorded in `legacy/`. Active tests and validators must
read from part paths, not from legacy.
