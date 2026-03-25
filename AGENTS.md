# AGENTS.md

Guidance for coding agents and humans contributing to `aoa-routing`.

## Purpose

`aoa-routing` is the thin navigation and dispatch layer for AoA.

It does not author new meaning.
It derives small routing surfaces that point agents to the next source-owned object without copying source corpora into a second canon.

## Owns

This repository is the source of truth for:

- routing projections
- dispatch hints
- recommended path surfaces
- local routing schemas
- routing validation logic
- integrity checks that keep navigation aligned with source-owned surfaces

## Does not own

Do not treat this repository as the source of truth for:

- technique meaning in `aoa-techniques`
- skill meaning in `aoa-skills`
- eval meaning in `aoa-evals`
- memory objects in `aoa-memo`
- role contracts in `aoa-agents`
- scenario composition in `aoa-playbooks`
- derived knowledge substrate semantics in `aoa-kag`

This repo owns navigation. It does not own the meaning of the things it routes to.

## Core rule

Source repos own meaning. Routing repo owns navigation.

If the task requires authored meaning, go to the source repository rather than recreating meaning here.

## Read this first

Before making changes, read in this order:

1. `README.md`
2. `generated/aoa_router.min.json`
3. `generated/task_to_surface_hints.json`
4. `generated/recommended_paths.min.json`
5. `ROADMAP.md`
6. builder or validator scripts only if the task touches generation logic

If the task affects ingestion contracts, inspect the relevant upstream generated catalogs before editing routing logic.

If you are editing inside `generated/`, `schemas/`, `scripts/`, or `tests/`, also follow the nested `AGENTS.md` in that directory.

## Primary objects

The most important objects in this repository are:

- `scripts/build_router.py`
- `scripts/router_core.py`
- `scripts/validate_router.py`
- `schemas/*`
- `generated/*.json`
- tests that validate router output integrity

## Allowed changes

Safe, normal contributions include:

- improving routing clarity and determinism
- improving dispatch hints
- improving recommended-path generation
- tightening validation and integrity checks
- refining ingestion contracts without violating source ownership
- improving error reporting around missing or drifted source surfaces

## Changes requiring extra care

Use extra caution when:

- changing generated output shape
- changing routeable object assumptions
- changing kind handling
- changing inspect-action logic
- changing dependency logic across repositories
- introducing any feature that makes routing behave like a second source of truth

## Hard NO

Do not:

- copy source text into routing outputs unless the repository canon explicitly allows it
- store memory here
- store eval doctrine here
- store workflow authoring here
- turn routing into a graph/KAG platform
- make routing authoritative over source meaning
- silently widen routing into a repo that “understands” content better than the source repo itself

## Routing doctrine

A good routing change should make it easier for an agent to answer:

- what kind of surface is needed
- what the smallest next object is
- which source-owned file should be inspected next
- what remains intentionally out of scope

A bad routing change usually makes routing heavier, more semantic, more duplicative, or more authoritative than it should be.

## Public hygiene

Assume routing outputs are public, inspectable, and contestable.

Write for portability:

- keep kind definitions explicit
- keep dispatch rules deterministic where possible
- prefer source-owned references over copied summaries
- make missing-source failure modes visible
- avoid hidden magic

## Contribution doctrine

Use this flow:

`PLAN -> DIFF -> VERIFY -> REPORT`

### PLAN

State:

- what routing surface or script is being changed
- which source repos are affected
- whether output shape changes
- what boundary risk exists

### DIFF

Keep the change focused.

Do not mix unrelated repository cleanup into routing logic changes unless it is necessary for repository integrity.

### VERIFY

Confirm that:

- source ownership is still preserved
- generated outputs remain deterministic
- inspect targets still point to source-owned surfaces
- no output is pretending to be a second source of truth
- tests and validators still pass

Rebuild generated outputs when the task affects generation logic.

### REPORT

Summarize:

- what changed
- which generated outputs changed
- whether output shape changed
- which source repos were involved
- any remaining follow-up work

## Validation

Run the documented build and validation commands from `README.md`.

If routing logic changes, rebuild generated outputs and run tests before finishing.
`python scripts/validate_router.py` also checks the nested local guidance surfaces in `generated/`, `schemas/`, `scripts/`, and `tests/`.

Do not claim validation you did not run.

## Cross-repo neighbors

Use these neighboring repositories when the task crosses boundaries:

- `aoa-techniques` for source practice meaning
- `aoa-skills` for execution workflow meaning
- `aoa-evals` for proof-surface meaning
- `aoa-memo` for future memory surfaces
- `Agents-of-Abyss` for ecosystem-level map and boundary doctrine

## Output expectations

When reporting back after a change, include:

- which routing scripts or surfaces changed
- whether generated outputs changed
- whether output shape changed
- what validation was run
- whether any source repo assumptions changed
- any boundary risks or follow-up work

## Default editing posture

Prefer the smallest reviewable change.
Preserve canonical wording unless the task explicitly requires semantic change.
If semantic change is made, report it explicitly.
