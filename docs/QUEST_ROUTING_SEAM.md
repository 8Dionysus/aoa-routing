# QUEST routing seam

## Purpose

This document defines how `aoa-routing` may assist quest discovery without becoming the author of quest meaning.

## Core rule

Source repos own quest meaning.
`aoa-routing` may only consume thin, derived quest projections from live generated quest surfaces.

It should not:
- parse live `quests/*.yaml` as authority
- reinterpret repo-local quest meaning
- invent priority or control semantics not published by the source repo
- turn routing hints into a new source-of-truth layer

## Preferred inputs

The first live quest-routing wave is source-only.
In this wave, routing may ingest only:

- `generated/quest_catalog.min.json`
- `generated/quest_dispatch.min.json`

Production routing does not read `.example.json` quest fixtures.

## Minimal routing actions

The only live quest actions in this wave are `inspect`, `expand`, and `handoff`.

Routing may help choose:
- `inspect` — open the source quest or questbook
- `expand` — open neighboring source-owned docs or parent quests
- `handoff` — route to the next source authority when a quest crosses repo boundaries

`pair` and `recall` belong to later routing waves.

## Tiny-model safe entry

Tiny-model-safe entry remains deferred in this wave.
The future safe routing posture for small local wrappers should stay narrow:
- `frontier` quests only
- `d0_probe` or `d1_patch` by default
- `r0_readonly` first, then bounded `r1_repo_local`
- always source-owned inspect paths first

## Anti-collapse rule

Routing is allowed to be useful.
Routing is not allowed to become the place where quest meaning is rewritten.
