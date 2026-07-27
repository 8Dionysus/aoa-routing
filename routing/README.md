# Routing Source Home

`routing/` retains the predecessor source-home for v1 compatibility and
rollback evidence.

It is not a head mechanic. Shared OS Abyss operations such as Agon,
Experience, Checkpoint, Recurrence, Questbook, Antifragility, Boundary Bridge,
Release Support, RPG, and Titan route through `mechanics/<head>/`.

The G5 owner-switch receipt governed by `AOA-RT-D-0004` has moved canonical
producer and ABI ownership to `aoa-sdk`. This source home is maintenance-only
for compatibility, security, rollback, and deprecation. M1 and M2 remain
historical transition evidence.

## Operating Card

| Field | Route |
| --- | --- |
| role | retained predecessor source-home for v1 compatibility and rollback |
| input | compatibility, security, rollback, deprecation, or source-home cleanup |
| output | bounded predecessor repair or route to canonical `aoa-sdk` owner |
| owner | `aoa-sdk` owns navigation producer and ABI; sibling repositories own meaning |
| next route | `aoa-sdk` for active work; `core/` only for allowed predecessor maintenance |
| validation | root maintenance gate plus source-home topology validation |

## Active Routes

| Route | Owns | Stronger split |
| --- | --- | --- |
| [`core/`](core/README.md) | retained v1 thin-router derivation used by compatibility and rollback | canonical work routes to `aoa-sdk`; source repos own object meaning |

The retained implementation may still read the historical skill surfaces when
exercised for rollback. It is not an active selector or producer path.

## Placement Rule

Route new routing behavior and public output work to `aoa-sdk`. Place only
allowed predecessor maintenance here; shared mechanics still route to
`mechanics/<head>/parts/`.

Former flat root paths are lookup facts, not active homes.
