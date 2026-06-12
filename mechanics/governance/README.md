# Governance

`mechanics/governance/` holds routing-local governance contracts for appeal,
veto, charter change, council dispatch, escalation, and precedent route hints.

## Operating Card

| Field | Route |
| --- | --- |
| role | route governance pressure without voting, vetoing, amending, or certifying |
| input | appeal packets, charter amendment routes, council cases, governance signals, precedent hints |
| output | bounded governance route packet or next owner/governance surface |
| owner | `aoa-routing` owns route shape only; owner law, council decision, sovereign review, and ToS intake stay with stronger owners |
| next route | `parts/appeal-and-veto/`, `parts/charter-change-routing/`, `parts/council-dispatch/`, `parts/governance-escalation/`, `parts/precedent-route-hints/` |
| validation | governance contract tests, mechanics topology validation |

## Boundary

Governance route parts produce reviewable navigation. They do not decide the
case, vote, veto, amend charters, or write doctrine.
