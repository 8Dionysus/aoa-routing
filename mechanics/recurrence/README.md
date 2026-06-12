# Recurrence

`mechanics/recurrence/` holds routing-local return navigation, downstream
recurrence hints, and incident re-entry contracts.

## Operating Card

| Field | Route |
| --- | --- |
| role | route recurrence pressure back to source-owned return, owner, or incident re-entry surfaces |
| input | return-navigation read model, recurrence projection, incident re-entry route, checkpoint/memo/source-owner stop lines |
| output | bounded return hint, downstream recurrence projection, or incident re-entry candidate route |
| owner | `aoa-routing` owns navigation shape; recurrence law, memory truth, proof, runtime policy, and source meaning stay with stronger owners |
| next route | `parts/return-navigation/`, `parts/downstream-hints/`, `parts/incident-reentry/` |
| validation | router validation, operation contract tests, mechanics topology validation |

## Boundary

Recurrence route parts do not decide whether return is justified. They point to
the smallest source-owned route once recurrence pressure reaches the router.
