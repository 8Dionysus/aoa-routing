# Release Support

`mechanics/release-support/` preserves predecessor release gate, deployment
ring, installation, and watchtower escalation contracts.

## Operating Card

| Field | Route |
| --- | --- |
| role | preserve predecessor release-support contracts and route current work to `aoa-sdk` |
| input | release gate decisions, deployment signals, installation route plans, watchtower escalation routes, release runbook |
| output | historical lookup or `aoa-sdk` handoff |
| owner | `aoa-sdk` owns active routing release support; stronger owners retain deployment, proof, runtime, and source authority |
| next route | `aoa-sdk` for active work; retained `parts/` only for historical inspection |
| validation | release contract tests, release check, mechanics topology validation |

## Boundary

These retained route parts do not authorize another predecessor release or
perform deployment. Active routing release support belongs in `aoa-sdk`.
