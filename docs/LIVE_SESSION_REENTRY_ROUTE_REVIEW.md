# Live Session Reentry Route Review

This note defines the explicit owner-local review surface for post-W10
live-session reentry routing in `aoa-routing`.

It is a routing-owned candidate surface.
It is not continuity truth, not runtime resume authority, not budget policy,
and not replay legitimacy proof.

## Core law

Source repos own meaning.
Routing owns navigation.

For live-session reentry, routing may publish one bounded review surface that
names:

- a `receipt_ref`
- a `route_reason`
- a `loop_guard`
- a `budget_ref`

That surface may reference a budget.
It must not define or mutate budget policy.

## Intended use

Use this surface when a reviewed continuity or checkpoint artifact makes a
bounded live-session reentry route legible, but the next hop still needs to
stay source-owned and reviewable.

The routing layer may:

- point to the next source-owned review surface
- carry one bounded route reason
- preserve a loop guard for reentry escalation
- carry a budget reference that remains owned elsewhere
- use a source-owned fallback review surface when the first route is not enough

The routing layer must not:

- approve direct runtime resume
- decide whether continuity is legitimate
- grant replay integrity
- invent budget policy
- replace owner review with router-owned state
- fall back to a router-owned surface

## Contract surfaces

This landing adds one compact contract pair:

- `schemas/live-session-reentry-route-review.schema.json`
- `examples/live_session_reentry_route_review.example.json`

The contract stays candidate-only.
It does not open a live loop.

## Neighbor boundaries

- `docs/RECURRENCE_NAVIGATION_BOUNDARY.md` remains the governing routing
  doctrine for return posture.
- `docs/ADOPTION_REENTRY_ROUTING.md` remains the adoption-specific reentry
  doctrine.
- `aoa-memo` owns checkpoint and continuity support meaning.
- `aoa-agents` owns continuity-run posture.
- `aoa-evals` owns replay and runtime integrity proof.
- `Agents-of-Abyss` owns the v2.0 center law and budget authority boundary.

## One-line rule

Routing may reference a reviewed receipt and a budget ref for live-session
reentry.
It must not become the owner of either one.
