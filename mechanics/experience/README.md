# Experience

`mechanics/experience/` holds routing-local office, service, adoption, and
certification route contracts.

## Operating Card

| Field | Route |
| --- | --- |
| role | route Experience work toward the owner that can approve, repair, adopt, certify, or operate it |
| input | office/service/adoption/certification docs, schemas, examples, and stronger-owner stop lines |
| output | typed route signal, gate, handoff packet, owner fanout, or certification owner route |
| owner | `aoa-routing` owns route shape only; AoA center, playbooks, evals, agents, runtime owners, and ToS keep stronger meaning |
| next route | `parts/office-route-gate/`, `parts/service-handoff/`, `parts/adoption-routing/`, `parts/certification-owner-landing/` |
| validation | Experience operation contract tests plus mechanics topology validation |

## Boundary

Experience route parts do not certify truth, operate services, approve release,
or write Tree of Sophia runtime/source surfaces. They make owner-local route
contracts explicit.
