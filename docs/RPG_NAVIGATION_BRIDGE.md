# RPG Navigation Bridge

## Purpose

This note defines the bridge-wave RPG navigation seam for `aoa-routing`.

It exists so routing can render one compact derived card that points to source quest, playbook party template, and unlock proof surfaces without becoming the author of any of those meanings.

## Core rule

Routing owns navigation.
Routing does not own quest meaning, unlock proof, or party doctrine.

A bridge-wave RPG navigation card may:
- summarize a source-owned quest or route in RPG-facing language
- point to `inspect`, `expand`, and `handoff`
- carry a derived party hint
- carry a derived loadout hint
- carry a derived unlock hint
- carry a derived reanchor hint

It must not:
- accept, claim, or complete quests
- award or revoke unlocks
- invent reward logic
- replace playbook or eval authority
- treat example cards as live dispatch authority

## Preferred inputs

This bridge-wave seam should consume only derived owner surfaces.

Preferred inputs once live owner builders exist:
- source quest dispatch surfaces
- source quest catalog surfaces
- `aoa-playbooks` generated party-template cards
- `aoa-evals` generated unlock-proof cards

In this seed pack the bundle remains example-only.

## Action vocabulary

Keep the action vocabulary narrow:
- `inspect`
- `expand`
- `handoff`

Do not add reward verbs, completion verbs, or state-writing verbs here.

## Party and unlock hints

Party and unlock hints must stay explicitly derived.

Good posture:
- point to the source template or proof object
- summarize required roles or abilities compactly
- keep cautions visible
- keep the card readable by a small model or frontend reader

## Tiny-model posture

The bridge-wave card may later help tiny local wrappers, but it should stay source-first and narrow.
Until live builders exist, keep this seam example-only and validator-shaped.

## Anti-patterns

- parse live quest YAML as authority from inside routing
- hide stronger meaning inside a card than the sources support
- let example cards become production truth by inertia
- widen routing into a reward, reputation, or orchestration throne
