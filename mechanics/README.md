# Mechanics

`mechanics/` is the active operation atlas for `aoa-routing` participation in
shared OS Abyss mechanics.

Local thin-router behavior starts in [`routing/`](../routing/README.md). A
mechanic exists here only when the repo owns a repeatable routing part of a
shared operation.

## Operating Card

| Field | Route |
| --- | --- |
| role | route shared mechanic pressure to the owning parent and part |
| input | mechanic-owned route docs, schemas, examples, config, manifests, generated companions, scripts, tests, or former flat path |
| output | active parent mechanic, active part, source-home handoff, provenance bridge, or legacy lookup |
| owner | parent package docs and part contracts; stronger OS Abyss owners keep final meaning |
| next route | `routing/` for local router source behavior, `QUESTBOOK.md` and `quests/` for source quest records, `mechanics/<head>/` for shared mechanic parts, `PROVENANCE.md` for former-path accounting |
| validation | mechanics topology checks and owning part validators |

## Active Parent Candidates

The first landing will activate only parents with evidenced payload clusters.
Candidate parents from current file inventory are:

| Parent | Current pressure |
| --- | --- |
| `agon` | gate routing, trigger model, decision boundary, assistant escalation, owner handoffs, recurrence adapter |
| `experience` | office, service, adoption, certification, governance-facing route gates |
| `checkpoint` | live-session reentry route review and checkpoint-starter handoff pressure |
| `recurrence` | return navigation, downstream hints, incident/adoption reentry |
| `questbook` | quest source-record operation law, quest routing seam, quest board seam, harvest fanout |
| `boundary-bridge` | federation entry, cross-repo bridge, owner dispatch, ToS/KAG boundaries |
| `antifragility` | stress posture, degraded hints, rollback, quarantine, suppression, via negativa |
| `release-support` | release gate, deployment ring, installation route |
| `titan` | Titan runtime, console, memory, app-server, runtime case routes |
| `rpg` | RPG navigation bridge |

Candidate means "evidenced by current payloads", not yet "fully landed".
Activation requires parent docs, `PARTS.md`, provenance, legacy accounting when
flat paths move, and validation.

## Placement Rule

Use the nearest operation owner:

- router source behavior -> `routing/`;
- routing quest source records -> `QUESTBOOK.md` and `quests/<lane>/<state>/`;
- shared mechanic operation -> `mechanics/<head>/parts/<part>/`;
- repo-wide release/validation/platform support -> root support districts;
- former flat path lookup -> package `PROVENANCE.md` then `legacy/`.

Do not preserve a root flat path as active just because it existed before.
