# AGENTS.md

This directory owns source quest record placement for `aoa-routing`.

`QUESTBOOK.md` is the human open-obligation index. `quests/` is the durable
source-record district. `mechanics/questbook/` owns operation law, validation
posture, and routing support for quest surfaces.

Do not move source quest records into mechanic parts. Mechanic parts may own
schemas, generated readers, validators, examples, and routing seams; durable
quest records stay here unless a stronger source-home decision says otherwise.

## Layout

Use lane-first lifecycle paths:

```text
quests/<lane>/<state>/<quest-file>
```

Current lanes:

- `routing/`: schema-backed `AOA-RT-Q-*.yaml` routing obligations.
- `agon/`: Agon gate-routing follow-through notes with current repo-qualified
  IDs when such notes are opened.

Historical Agon receipts are not active quest records. They are reached through
Agon provenance and package-local legacy raw surfaces.

Current lifecycle states are `captured`, `triaged`, `ready`, `active`,
`blocked`, `reanchor`, `done`, and `dropped`.

## Verify

Run:

```bash
python scripts/validate_router.py
python scripts/validate_semantic_agents.py
python -m pytest -q tests/test_validate_router.py
```
