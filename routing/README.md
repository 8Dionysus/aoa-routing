# Routing Source Home

`routing/` is the source-home district for local `aoa-routing` navigation
behavior.

It is not a head mechanic. Shared OS Abyss operations such as Agon,
Experience, Checkpoint, Recurrence, Questbook, Antifragility, Boundary Bridge,
Release Support, RPG, and Titan route through `mechanics/<head>/`.

## Operating Card

| Field | Route |
| --- | --- |
| role | local source-home for thin routing, public output derivation, and routing-only seams |
| input | route derivation, source catalog ingestion, low-context routing policy, generated-output parity, or source-home cleanup |
| output | source-home contract, public generated routing output, root compatibility wrapper, or mechanics handoff |
| owner | `aoa-routing` owns navigation; sibling repositories own meaning |
| next route | `core/`, `two-stage-skill-selection/`, root `generated/`, or `mechanics/` for shared mechanic participation |
| validation | root route validators plus source-home topology validation when active |

## Active Routes

| Route | Owns | Stronger split |
| --- | --- | --- |
| [`core/`](core/README.md) | thin-router derivation, cross-repo registry, task/surface/tier hints, recommended paths, pairing, owner shortlist, and federation-return builder behavior | source repos own object meaning; root `generated/` may remain public output |
| [`two-stage-skill-selection/`](two-stage-skill-selection/README.md) | optional routing-local stage-1 shortlist and stage-2 skill decision seam | `aoa-skills` owns skill source meaning and activation posture |

## Placement Rule

When a file-name cluster is local routing behavior, route it here. When it is a
functioning part of a shared mechanic, route it to `mechanics/<head>/parts/`.
When it is a public output consumed across repositories, it may remain
root-published under `generated/` while its builder, contract, and provenance
route through the owning source home or part.

Former flat root paths are lookup facts, not active homes.
