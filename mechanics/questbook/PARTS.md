# Questbook Parts

## source-contract

| Field | Route |
| --- | --- |
| role | define the local source-record contract and validation posture |
| input | `QUESTBOOK.md`, `quests/routing/<state>/AOA-RT-Q-*.yaml`, and route-law pressure |
| output | source-record validation, placement rules, and handoff to owning parts |
| owner | `mechanics/questbook/parts/source-contract/` |
| next route | `QUESTBOOK.md`, `quests/`, owning quest part, source repo, or route validator |
| verification | `validate_local_questbook_surfaces` |

## quest-routing-seam

| Field | Route |
| --- | --- |
| role | publish source-only quest routing rules and schemas |
| input | sibling `generated/quest_catalog.min.json` and `generated/quest_dispatch.min.json` |
| output | `generated/quest_dispatch_hints.min.json` |
| owner | `mechanics/questbook/parts/quest-routing-seam/` |
| next route | source quest inspect, source-owned expand doc, or owner handoff |
| verification | `validate_local_questbook_surfaces` and generated-output validation |

## quest-board-seam

| Field | Route |
| --- | --- |
| role | keep example-only board-card reflection bounded |
| input | source quest dispatch, agent progression examples, eval progression evidence |
| output | example board entry payload |
| owner | `mechanics/questbook/parts/quest-board-seam/` |
| next route | source dispatch or future reviewed progression owner |
| verification | adjunct quest board validator |

## harvest-fanout

| Field | Route |
| --- | --- |
| role | route reviewed harvest pressure into owner-local quest creation |
| input | recurrence, evidence, owner landing, bounded verdict, retention pressure |
| output | route signal for reviewed owner-local quest fanout |
| owner | `mechanics/questbook/parts/harvest-fanout/` |
| next route | owner repo, KAG promotion, ToS dossier boundary, eval verdict |
| verification | schema/example contract tests |
