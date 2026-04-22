# Agon Gate Decision Boundary

The Agon gate route is a candidate signal.

It is not activation.

## Decision states

`no_gate_service_route` means ordinary service or thin routing is still enough.

`agon_gate_candidate` means a future center-owned gate should review the case.

`agon_gate_candidate_missing_context` means routing lacks the signals needed for a meaningful gate candidate.

`owner_review_required` means an owning repository or proof layer must inspect the case first.

`quarantine_hint` means a boundary breach, hidden authority, or unsafe drift should be stopped or isolated before any arena path.

## Boundary

Routing may rank and point.

Routing may not judge and mutate.

The gate signal should stay legible, small, and reversible.

## Wave 1 owner dispatch seam

Wave 1 adds one compact seam for the route signal, route decision, and owner
dispatch handoff path:

- `schemas/owner-dispatch-seam.schema.json`
- `examples/owner_dispatch_seam.example.json`

The seam keeps three layers separate:

- `route_signal` is the candidate signal
- `route_decision` is the bounded navigation choice
- `owner_dispatch` is the handoff to the owning repo, not owner truth itself

Routing may point and hand off. It may not become the authority surface it
describes.
