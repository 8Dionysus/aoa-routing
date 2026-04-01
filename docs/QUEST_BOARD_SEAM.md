# Quest Board Seam

## Purpose

This note defines the first derived quest-board reflection seam for `aoa-routing`.

It exists so that routing can later render RPG-shaped quest cards without taking ownership of quest meaning, progression meaning, or campaign authority.

## Core rule

A quest-board entry is a derived hint object.

In this first wave it may:
- summarize one source quest for board-like reading
- point to inspect / expand / handoff actions
- carry a recommended party hint
- carry a progression-gate hint

In this first wave it must not:
- accept or claim quests
- write quest state
- award progression
- replace the source dispatch surface
- replace the source progression surface

## Source posture

Use existing source-owned quest and dispatch surfaces first.

A future quest-board entry may derive from:
- source quest catalog surfaces
- source quest dispatch surfaces
- reviewed progression examples or later progression projections
- reviewed campaign or chronicle references

The quest board does not become the source of any of those meanings.

## Entry actions

Keep the live action vocabulary narrow:

- `inspect`
- `expand`
- `handoff`

Do not add `accept`, `claim`, `complete`, or reward verbs in this wave.

## Party hint posture

A board entry may suggest:

- one cohort pattern
- likely roles
- likely tier path

These stay hints, not enforcement.

## Progression gate posture

A board entry may carry a derived progression-gate hint such as:

- minimum suggested rank
- preferred mastery axes
- caution note

These are derived hints only. Source progression and source quest authority remain upstream.

## Anti-patterns

- parsing live quest YAML as the new authority
- pretending a board card is the quest itself
- widening routing into reward logic
- turning one example board into a live service before builders exist
