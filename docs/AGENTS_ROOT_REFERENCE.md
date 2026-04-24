# AGENTS root reference

This file preserves the previous full root guidance for `aoa-routing`.
The live root route card is `../AGENTS.md`.

Use this reference when:

- auditing a legacy rule from before Pack 5
- resolving a task branch that the short route card intentionally summarized
- checking whether a slimming move should become a nested `AGENTS.md`, owner doc, or validator rule

Do not treat this file as a competing root. If a preserved rule still actively governs a local directory, move or restate it at the smallest owner surface rather than re-bloating the root.

## Preserved root AGENTS.md from before Pack 5

# AGENTS.md

Guidance for coding agents and humans contributing to `aoa-routing`.

## Purpose

`aoa-routing` is the thin navigation and dispatch layer for AoA.
It derives lightweight routing surfaces that point agents to the next
source-owned object without copying source corpora into a second canon.

This repository owns navigation.
It does not own the meaning of the things it routes to.

## Owns

This repository is the source of truth for:

- routing projections and registries
- dispatch hints and recommended paths
- advisory owner-layer shortlist hints
- bounded pairing, return-navigation, and low-context routing seams
- optional two-stage routing policy and tool/prompt surfaces
- additive stress-route overlays and quest-style routing adjunct examples when explicitly defined here
- local schemas, build scripts, validators, and integrity checks

## Does not own

Do not treat this repository as the source of truth for:

- technique meaning in `aoa-techniques`
- skill meaning in `aoa-skills`
- eval meaning in `aoa-evals`
- memory objects or recall doctrine in `aoa-memo`
- role contracts, progression policy, or checkpoint doctrine in `aoa-agents`
- scenario composition or live quest state in `aoa-playbooks`
- derived substrate semantics in `aoa-kag`
- federation-root identity or constitutional meaning in `Agents-of-Abyss`

## Core rules

Source repos own meaning.
Routing repo owns navigation.

If a task requires authored meaning, go to the owning repository instead of
recreating it here.

Routing hints may advertise owner-layer candidates, ambiguity, return posture,
quest-style seams, or stress overlays.
None of those become semantic truth, activation authority, or live quest
sovereignty at the routing layer.

## Read this first

Before making changes, read in this order:

1. `README.md`
2. `ROADMAP.md`
3. `generated/aoa_router.min.json`
4. `generated/task_to_surface_hints.json`
5. `generated/owner_layer_shortlist.min.json`
6. `generated/recommended_paths.min.json`
7. `generated/federation_entrypoints.min.json` when the task touches federation entry
8. `docs/TWO_STAGE_SKILL_SELECTION.md` when the task touches the optional wave-9 seam

Then branch by task:

- federation entry or bounded return posture:
  `docs/FEDERATION_ENTRY_ABI.md` and
  `docs/RECURRENCE_NAVIGATION_BOUNDARY.md`
- quest-style adjunct seams:
  `docs/QUEST_BOARD_SEAM.md` and
  `docs/QUEST_ROUTING_SEAM.md`
- stress overlays:
  `docs/STRESS_POSTURE_ROUTING.md`,
  `docs/DEGRADED_ROUTE_HINTS.md`,
  `docs/PLAYBOOK_STRESS_ROUTE_CONSUMPTION.md`, and
  `docs/KAG_QUARANTINE_ROUTE_HINTS.md`
- Agon gate routing:
  `docs/AGON_GATE_ROUTING.md`,
  `docs/AGON_GATE_TRIGGER_MODEL.md`,
  `docs/AGON_GATE_DECISION_BOUNDARY.md`,
  `docs/AGON_GATE_ASSISTANT_ESCALATION.md`, and
  `docs/AGON_GATE_ROUTING_OWNER_HANDOFFS.md`
- stage-two skill routing:
  the `two_stage_*` generated family and
  `docs/TWO_STAGE_SKILL_SELECTION.md`

If the task affects ingestion contracts, inspect the relevant upstream
generated catalogs before editing routing logic.

If you are editing inside `generated/`, `schemas/`, `scripts/`, or `tests/`,
also follow the nested `AGENTS.md` in that directory.

## Primary objects

The most important objects in this repository are:

- `scripts/build_router.py`
- `scripts/router_core.py`
- `scripts/validate_router.py`
- `scripts/build_agon_gate_routing_registry.py`
- `scripts/validate_agon_gate_routing.py`
- `scripts/build_two_stage_skill_router.py`
- `scripts/validate_two_stage_skill_router.py`
- `schemas/*`
- `generated/*.json`
- tests that validate routing integrity

## Hard NO

Do not:

- copy source text into routing outputs unless the repository canon explicitly allows it
- store memory, eval doctrine, or playbook authoring here
- let stage 1 activate a skill or override explicit-only posture
- let owner-layer shortlist hints become semantic truth or activation authority
- turn quest-board or dispatch-hint examples into live authority
- turn routing into a graph or KAG platform
- make routing authoritative over source meaning
- silently widen routing into a repo that appears to understand content better than the source repo itself

## Contribution doctrine

Use this flow: `PLAN -> DIFF -> VERIFY -> REPORT`

### PLAN

State:

- what routing surface or script is changing
- which source repositories are affected
- whether output shape changes
- whether stage-two, stress, return, Agon gate, or quest-style adjunct surfaces are changing
- what boundary risk exists

### DIFF

Keep the change focused.
Do not mix unrelated cleanup into routing logic changes unless it is necessary
for repository integrity.

### VERIFY

Run the documented commands from `README.md`.

For routing logic changes, rebuild generated outputs and run tests before
finishing:

```bash
python scripts/build_router.py
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python -m pytest -q tests
```

Confirm that:

- source ownership is still preserved
- generated outputs remain deterministic
- inspect and expand targets still point to source-owned surfaces
- no output behaves like a second source of truth
- quest-board, stress, and return surfaces remain advisory
- Agon gate surfaces remain pre-protocol and center-respecting
- stage 1 never becomes activation authority

### REPORT

Summarize:

- what changed
- which generated outputs changed
- whether output shape changed
- which source repositories were involved
- what validation you actually ran
- any remaining follow-up work

## Validation

Do not claim validation you did not run.
