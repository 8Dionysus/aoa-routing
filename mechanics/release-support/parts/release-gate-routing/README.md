# Release Gate Routing

Preserves predecessor release-gate decisions and the retired repo release
runbook. It owns no active maintenance or publication lane after `v0.4.0`.

Preserved payloads:

- `evidence/routing-succession-m3-maintenance-only.json`
- `docs/release-gate-routing.md`
- `docs/routing-succession-m3-maintenance-only.md`
- `docs/releasing.md`
- `schemas/routing-succession-m3-maintenance-only.schema.json`
- `schemas/routing-maintenance-approval.schema.json`
- `schemas/release_gate_route_decision_v1.json`
- `examples/release_gate_route_decision.example.json`
- `scripts/validate_routing_maintenance_only.py`

`evidence/maintenance-approvals/` records the exact reviewed deprecation
changes required to close the final archive boundary. Such packets bind the
review to the immutable M3 base, exact retained path, and exact resulting Git
blob. They do not authorize future predecessor maintenance or publication.

Historical M1, M2, and M3 transition evidence remains immutable under
`config/`, `docs/`, `evidence/`, `schemas/`, and `scripts/`. It is not an
active release or CI authority.
- `scripts/verify_sdk_shadow_release_parity.py`
