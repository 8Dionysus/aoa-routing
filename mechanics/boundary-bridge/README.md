# Boundary Bridge

`mechanics/boundary-bridge/` holds routing-local bridge contracts for federation
entry, owner-layer shortlist, cross-repo bridge, KAG/ToS boundary, harvest
routing, and stats re-grounding pressure.

## Operating Card

| Field | Route |
| --- | --- |
| role | route cross-repo boundary pressure without becoming source authority |
| input | federation entries, owner-layer signals, harvest route decisions, KAG/ToS boundary signals, stats-derived re-grounding hints |
| output | public routing output schema, route signal, or next owner read |
| owner | `aoa-routing` owns route shape only; source repos own meaning, proof, runtime, and canon |
| next route | `parts/federation-entry/`, `parts/cross-repo-router-bridge/`, `parts/owner-layer-shortlist/`, `parts/federation-harvest-routing/`, `parts/tos-kag-boundary/`, `parts/stats-regrounding/` |
| validation | router build/check, federation/owner/stats schema validation, mechanics topology validation |

## Boundary

Boundary-bridge parts publish navigation and re-grounding pressure. They do not
approve promotion, write ToS canon, certify stats, or replace source-owned
capsules.
