# Quest Source Records

`quests/` is the source quest record district for `aoa-routing` obligations
that should survive a diff.

It is not a private scratchpad and not a second roadmap. Program direction
belongs in `ROADMAP.md`. Human open-obligation visibility belongs in
`QUESTBOOK.md`. Questbook operation law starts in `mechanics/questbook/`.

Quest sources live in lane-first lifecycle directories:

```text
quests/<lane>/<state>/<quest-file>
```

## Operating Card

| Field | Route |
| --- | --- |
| role | routing source quest record district |
| input | durable routing obligation, reviewed handoff, deferred route pressure, or Agon gate follow-through |
| output | lane/state source record, `QUESTBOOK.md` open-obligation entry, or handoff to an owning mechanic part |
| owner | `quests/AGENTS.md` for editing law; `mechanics/questbook/` for operation posture |
| next route | `QUESTBOOK.md`, `quests/<lane>/<state>/`, `mechanics/questbook/`, or the owning mechanic part |
| validation | `python scripts/validate_router.py` |

## Lanes

| Lane | Use |
| --- | --- |
| `routing/` | schema-backed `AOA-RT-Q-*.yaml` records for router-owned quest-dispatch, board, and navigation obligations |
| `agon/` | Agon gate-routing follow-through notes with current repo-qualified IDs |

## Lifecycle States

Each lane may contain:

| State | Use |
| --- | --- |
| `captured` | public-safe obligation exists, but route shaping is not complete |
| `triaged` | route-bearing obligation with enough shape to split, promote, or close |
| `ready` | next owner action is clear and bounded |
| `active` | currently being advanced by an owner lane |
| `blocked` | waiting on a named dependency or owner decision |
| `reanchor` | old route no longer matches; choose a new owner, band, or evidence path |
| `done` | landed with enough public evidence to leave the active index |
| `dropped` | intentionally closed without landing, with a visible reason |

## Boundaries

- `QUESTBOOK.md` owns human open-obligation visibility.
- `quests/` owns source quest record placement.
- `mechanics/questbook/` owns routing-local questbook operation law.
- Historical Agon receipts are legacy raw records reached through Agon
  provenance, not active `quests/` entries.
- Mechanic parts own their docs, schemas, examples, config, generated
  companions, scripts, tests, and route seams.
- Generated quest hints derive from source-owned upstream records; they do not
  author quest meaning.
