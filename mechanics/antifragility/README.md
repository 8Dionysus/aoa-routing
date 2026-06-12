# Antifragility

`mechanics/antifragility/` holds routing-local stress, rollback, quarantine, and
negative-check parts.

## Operating Card

| Field | Route |
| --- | --- |
| role | route stressed or unsafe movement toward the bounded owner surface |
| input | owner receipts, explicit eval/proof, playbook/KAG stress surfaces, rollback signals, suppression state |
| output | navigation posture, bounded next hop, rollback or hold route, or suppressed hint |
| owner | `aoa-routing` owns route shape only; source repos own stress meaning |
| next route | `parts/stress-routing/`, `parts/degraded-route-hints/`, `parts/composite-stress-routing/`, `parts/quarantine-routing/`, `parts/rollback-routing/`, `parts/via-negativa/` |
| validation | antifragility schema tests, router schema validation, mechanics topology validation |

## Boundary

Antifragility route parts do not decide health, repair, or policy. They name the
next safe owner route when evidence is already bounded enough to act.
