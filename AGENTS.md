# AGENTS.md

Guidance for coding agents and humans contributing to `aoa-routing`.

## Purpose

`aoa-routing` is the thin navigation and dispatch layer for AoA. It derives small routing surfaces that point agents to the next source-owned object without copying source corpora into a second canon.

## Owns

This repository is the source of truth for:

- routing projections and registries
- dispatch hints and recommended paths
- bounded pairing, return-navigation, and low-context routing seams
- local schemas, build scripts, validators, and integrity checks

## Does not own

Do not treat this repository as the source of truth for:

- technique meaning in `aoa-techniques`
- skill meaning in `aoa-skills`
- eval meaning in `aoa-evals`
- memory objects or recall doctrine in `aoa-memo`
- role contracts in `aoa-agents`
- scenario composition in `aoa-playbooks`
- derived substrate semantics in `aoa-kag`

This repo owns navigation. It does not own the meaning of the things it routes to.

## Core rule

Source repos own meaning. Routing repo owns navigation.

If a task requires authored meaning, go to the owning repository instead of recreating it here.

## Read this first

Before making changes, read in this order:

1. `README.md`
2. `generated/aoa_router.min.json`
3. `generated/task_to_surface_hints.json`
4. `generated/recommended_paths.min.json`
5. `generated/federation_entrypoints.min.json` if the task touches federation entry
6. `docs/TWO_STAGE_SKILL_SELECTION.md` if the task touches wave-9
7. builder or validator scripts only if the task touches generation logic

If the task affects ingestion contracts, inspect the relevant upstream generated catalogs before editing routing logic.

If you are editing inside `generated/`, `schemas/`, `scripts/`, or `tests/`, also follow the nested `AGENTS.md` in that directory.

## Primary objects

The most important objects in this repository are:

- `scripts/build_router.py`
- `scripts/router_core.py`
- `scripts/validate_router.py`
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
- what boundary risk exists

### DIFF

Keep the change focused. Do not mix unrelated cleanup into routing logic changes unless it is necessary for repository integrity.

### VERIFY

Confirm that:

- source ownership is still preserved
- generated outputs remain deterministic
- inspect and expand targets still point to source-owned surfaces
- no output behaves like a second source of truth
- tests and validators still pass when generation logic changes

### REPORT

Summarize:

- what changed
- which generated outputs changed
- whether output shape changed
- which source repositories were involved
- any remaining follow-up work

## Validation

Run the documented commands from `README.md`.

When routing logic changes, rebuild generated outputs and run tests before finishing.

The core commands are:

```bash
python scripts/build_router.py
python scripts/validate_router.py
pytest
```

`python scripts/validate_router.py` also checks the local guidance surfaces in `generated/`, `schemas/`, `scripts/`, and `tests/`.

Do not claim validation you did not run.
