# Questbook

This mechanic contains routing-owned support for source-owned quest discovery.

`aoa-routing` helps find and dispatch to quests. It does not own quest meaning,
quest priority, progression, acceptance, or reward logic.

## Parts

- `source-contract`: the local `aoa-routing` questbook and quest records.
- `quest-routing-seam`: source-only inspect/expand/handoff routing from sibling
  generated quest surfaces.
- `quest-board-seam`: example-only board reflection for RPG-shaped cards.
- `harvest-fanout`: route signal for owner-local quest creation after reviewed
  federation harvest.

## Owner Split

Source repos own their quests. `aoa-routing` owns only derived navigation hints
and checks that those hints stay source-owned.
