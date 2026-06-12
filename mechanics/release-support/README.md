# Release Support

`mechanics/release-support/` holds routing-local release gate, deployment ring,
installation, and watchtower escalation contracts.

## Operating Card

| Field | Route |
| --- | --- |
| role | route release and installation pressure to the owner, gate, watch, or support surface that can act |
| input | release gate decisions, deployment signals, installation route plans, watchtower escalation routes, release runbook |
| output | release gate route, deployment route signal, installation route plan, watchtower escalation route |
| owner | `aoa-routing` owns route shape only; CI, GitHub, runtime deployment, proof, and source authority stay with stronger owners |
| next route | `parts/release-gate-routing/`, `parts/deployment-ring-routing/`, `parts/installation-routing/`, `parts/watchtower-escalation/` |
| validation | release contract tests, release check, mechanics topology validation |

## Boundary

Release-support route parts do not certify a release or perform deployment. They
make the next bounded release-support route explicit.
