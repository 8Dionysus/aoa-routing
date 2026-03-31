# QUEST routing seam

## Purpose

This document defines how `aoa-routing` may assist quest discovery without becoming the author of quest meaning.

## Core rule

Source repos own quest meaning.
`aoa-routing` may only consume thin, derived quest projections.

It should not:
- parse live `quests/*.yaml` as authority
- reinterpret repo-local quest meaning
- invent priority or control semantics not published by the source repo
- turn routing hints into a new source-of-truth layer

## Preferred inputs

Once a repo is ready, routing may ingest:

- `generated/quest_catalog.min.json`
- `generated/quest_dispatch.min.json`

Until builders exist, repos may temporarily carry `.example.json` seed files, but routing should not depend on them in production.

## Minimal routing actions

Routing may help choose:
- `inspect` — open the source quest or questbook
- `expand` — open neighboring source-owned docs or parent quests
- `pair` — suggest a planner/verifier handoff when a quest is not leaf-safe
- `recall` — route toward memo only when a quest names memory-relevant evidence or witness traces
- `handoff` — route to the next source authority when a quest crosses repo boundaries

## Tiny-model safe entry

The first safe routing posture for small local wrappers should be narrow:
- `frontier` quests only
- `d0_probe` or `d1_patch` by default
- `r0_readonly` first, then bounded `r1_repo_local`
- always source-owned inspect paths first

## Anti-collapse rule

Routing is allowed to be useful.
Routing is not allowed to become the place where quest meaning is rewritten.
