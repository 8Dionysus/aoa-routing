# Agon

Agon in this repository is a thin routing mechanic. It helps ordinary routing
notice when a task may need center-owned Agon review while preserving the
boundary that `aoa-routing` only points, ranks, and hands off.

## Operational Map

| Field | Value |
| --- | --- |
| Role | Pre-protocol gate candidate routing and owner-review handoff. |
| Input | Gate trigger config, owner dispatch seam example, optional sibling Agon registries. |
| Output | Part-local Agon gate routing registry and recurrence observation manifest. |
| Owner | `aoa-routing` owns the route hint; `Agents-of-Abyss` owns Agon sovereignty. |
| Next route | Center review, owner repo review, or ordinary service route depending on trigger state. |
| Tools | Part-local builder, validator, and tests under `parts/gate-routing/`. |
| Verification | executable route in root `AGENTS.md` and the gate-routing part tests |

## Parts

See `PARTS.md` for the active tree. Former root paths and the historical gate-routing
landing note are accounted for in `legacy/`, not used as active behavior.
