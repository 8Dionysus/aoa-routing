# Routing Source Home

`routing/` is the source-home district for local `aoa-routing` navigation
behavior.

It is not a head mechanic. Shared OS Abyss operations such as Agon,
Experience, Checkpoint, Recurrence, Questbook, Antifragility, Boundary Bridge,
Release Support, RPG, and Titan route through `mechanics/<head>/`.

This source home remains canonical until the G5 owner-switch receipt accepted
by `AOA-RT-D-0004`. After G5 it becomes maintenance-only for compatibility,
security, rollback, and deprecation; new routing features route to `aoa-sdk`.

## Operating Card

| Field | Route |
| --- | --- |
| role | local source-home for thin routing, public output derivation, and routing-only seams |
| input | route derivation, source catalog ingestion, low-context routing policy, generated-output parity, or source-home cleanup |
| output | source-home contract, public generated routing output, root compatibility wrapper, or mechanics handoff |
| owner | `aoa-routing` owns navigation; sibling repositories own meaning |
| next route | `core/`, root `generated/`, or `mechanics/` for shared mechanic participation |
| validation | root route validators plus source-home topology validation when active |

## Active Routes

| Route | Owns | Stronger split |
| --- | --- | --- |
| [`core/`](core/README.md) | thin-router derivation, cross-repo registry, task/surface/tier hints, recommended paths, pairing, owner shortlist, and federation-return builder behavior | source repos own object meaning; root `generated/` may remain public output |

Skill routing is part of the core ingestion path: the compact callable-bundle
cut comes from `aoa-skills/generated/agent_skill_catalog.min.json`, while deep
capability navigation routes to
`aoa-skills/generated/capability_graph.json`. `aoa-routing` does not own a
second skill selector or a persisted task execution DAG.

## Placement Rule

When a file-name cluster is local routing behavior, route it here. When it is a
functioning part of a shared mechanic, route it to `mechanics/<head>/parts/`.
When it is a public output consumed across repositories, it may remain
root-published under `generated/` while its builder, contract, and provenance
route through the owning source home or part.

Former flat root paths are lookup facts, not active homes.
