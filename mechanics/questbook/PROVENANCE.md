# Questbook Provenance

## Source Record Correction

`QUESTBOOK.md` and durable quest records remain active root source-record
surfaces. They were briefly treated as part-local payloads during the mechanics
refactor, then restored to match the refactored AoA questbook pattern.

Current active source record routes:

- `QUESTBOOK.md`
- `quests/routing/done/AOA-RT-Q-0001.yaml`
- `quests/routing/reanchor/AOA-RT-Q-0002.yaml`
- `quests/routing/captured/AOA-RT-Q-0003.yaml`
- `quests/routing/triaged/AOA-RT-Q-0004.yaml`

Historical Agon receipts are not active quest records. They live under
`../agon/legacy/raw/` and are reached through Agon provenance.

## Former Flat Paths

- `quests/AOA-RT-Q-0001.yaml`
- `quests/AOA-RT-Q-0002.yaml`
- `quests/AOA-RT-Q-0003.yaml`
- `quests/AOA-RT-Q-0004.yaml`
- `docs/QUEST_ROUTING_SEAM.md`
- `docs/QUEST_BOARD_SEAM.md`
- `docs/HARVEST_QUEST_FANOUT.md`
- `schemas/quest_dispatch_hint.schema.json`
- `schemas/quest-dispatch-hints.schema.json`
- `schemas/quest_board_entry.schema.json`
- `schemas/harvest_quest_fanout_v1.json`
- `examples/harvest_quest_fanout.example.json`
- `generated/quest_board.min.example.json`

## Current Active Parts

- `parts/source-contract/`
- `parts/quest-routing-seam/`
- `parts/quest-board-seam/`
- `parts/harvest-fanout/`

Root `generated/quest_dispatch_hints.min.json` remains a public routing output.
Root `QUESTBOOK.md` and `quests/` remain active source-record surfaces.

## Legacy Boundary

Former flat paths are recorded in `legacy/`. Active validators and builders must
read from root source-record surfaces or active parts, not from legacy.
