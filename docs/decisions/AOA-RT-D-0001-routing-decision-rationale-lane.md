# Routing Decision Rationale Lane

## Index Metadata

- Decision ID: AOA-RT-D-0001
- Original date: 2026-06-04
- Surface classes: docs/decisions, docs/route-law, scripts/validation, tests/route-law
- Routing surfaces: decision lane, thin router, generated indexes
- Source lanes: routing, sibling owners
- Guard families: source-owned authority, generated index parity, owner boundary
- Posture: accepted

## Context

`aoa-routing` already has strong current surfaces for routing output, route-law docs, schemas, examples, validators, and generated parity. Those surfaces answer what the router does and whether it stayed thin.

They do not always preserve why a route boundary, generated-output policy, owner handoff, fallback posture, or validator lane was chosen. As routing grows across federation entry, recurrence return, stress overlays, Agon gate routing, and optional two-stage skill routing, future agents need durable rationale without mistaking that rationale for generated routing authority.

Sibling AoA repositories now use generated decision indexes to keep durable rationale discoverable. `aoa-routing` should take the discoverability pattern while keeping the local language centered on navigation, source lanes, and owner-boundary guards.

## Decision

Adopt `docs/decisions/` as the durable `aoa-routing` decision-rationale lane.

Decision records use canonical `AOA-RT-D-####` IDs, full canonical-ID filenames, and an `## Index Metadata` block. Generated lookup indexes under `docs/decisions/indexes/` expose records by number, date, surface class, routing surface, source lane, and guard family.

Decision records explain why a route was chosen. They do not replace current generated outputs, schemas, examples, validators, tests, or sibling source authority.

## Options Considered

- Keep rationale only in route docs and tests. This keeps the surface count small, but future agents must rediscover durable decisions across many route documents.
- Copy a sibling decision lane literally. This gives superficial symmetry, but imports non-routing vocabulary that does not fit the navigation/source-owner boundary.
- Create a routing-local generated-indexed decision lane. This preserves sibling discoverability while keeping local owner language honest.

## Rationale

`aoa-routing` is repeatedly asked to make boundary choices: what counts as navigation versus meaning, which generated surface is advisory, when a fallback should remain bounded, and where a source-owned owner keeps authority.

Those choices deserve durable rationale, but the rationale must not become dispatch authority. The selected lane keeps decisions findable while requiring agents to route back to generated outputs, schemas, examples, validators, tests, or sibling owner repositories for current truth.

The metadata is routing-specific:

- `Routing surfaces` names thin-router, federation-entry, return-navigation, stress, Agon gate, two-stage, decision-lane, or generated-index pressure.
- `Source lanes` names the owning route family or sibling owner pressure that shaped the handoff.
- `Guard families` names source-owned authority, generated parity, owner boundary, fallback posture, low-context, or activation stop-line pressure.

## Consequences

New durable route-law, owner-boundary, generated-output, fallback, validator, or optional routing-seam decisions should land as `AOA-RT-D-####` notes when the rationale would otherwise be hard to reconstruct.

Existing route docs remain route docs. They do not need retroactive conversion.

If a decision changes, a new decision supersedes the old one. Existing IDs and filenames are not renumbered.

Generated indexes must stay derived from decision metadata and must not be hand-edited.

## Source Surfaces

- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `tests/AGENTS.md`
- `scripts/validate_nested_agents.py`
- `scripts/release_check.py`

## Validation

Current executable checks are owned by `docs/decisions/AGENTS.md`, root
`AGENTS.md`, and the decision-index scripts. The original landing also used the
repo-level verifier because the lane added route-law and validation surfaces.
