# aoa-routing

Thin navigation, typing, and dispatch layer for the public AoA stack.

`aoa-routing` does not author new meaning.
It derives lightweight routing surfaces from sibling AoA repositories so models can
decide what to read next without loading each corpus raw.

The core rule for this repository is:

**Source repos own meaning. Routing repo owns navigation.**

The current runtime path is:

`pick -> inspect -> expand -> object use`

## Scope

`aoa-routing` v0.1 covers:

- `aoa-techniques` as the practice canon
- `aoa-skills` as the execution canon
- `aoa-evals` as the proof canon

`aoa-memo` is reserved as a future `kind`, but v0.1 does not ingest concrete memo objects.

## Current ingestion model

The build reads only repo-local generated catalogs:

- `aoa-techniques` from `generated/technique_catalog.min.json`
- `aoa-skills` from `generated/skill_catalog.min.json`
- `aoa-evals` from `generated/eval_catalog.min.json`

`aoa-routing` no longer parses live `SKILL.md`, `techniques.yaml`, `EVAL.md`, or `eval.yaml`.
That contract keeps source meaning inside the source repositories while letting routing stay
deterministic and small.

Explicit `AOA-T-PENDING-*` technique placeholders are allowed in source manifests.
They remain future-only references and do not produce concrete `recommended_paths`
until the upstream technique exists in `aoa-techniques`.

## Generated outputs

The builder writes these tracked artifacts under `generated/`:

- `cross_repo_registry.min.json` - normalized registry of all routeable objects
- `aoa_router.min.json` - minimal entry routing projection
- `task_to_surface_hints.json` - static dispatch hints by surface kind, including inspect and expand actions
- `recommended_paths.min.json` - bounded cross-kind upstream/downstream hops

Inspect actions point to repo-local capsule surfaces:

- `aoa-techniques/generated/technique_capsules.json`
- `aoa-skills/generated/skill_capsules.json`
- `aoa-evals/generated/eval_capsules.json`

`aoa-routing` does not copy capsule text into its own outputs.
It only tells an agent which source-owned surface to inspect next.

Expand actions point to repo-local section surfaces:

- `aoa-techniques/generated/technique_sections.full.json`
- `aoa-skills/generated/skill_sections.full.json`
- `aoa-evals/generated/eval_sections.full.json`

`aoa-routing` does not copy section payloads into its own outputs.
It only tells an agent which source-owned section surface to expand next.

## Repository layout

- `scripts/` - builder, validator, and shared helpers
- `schemas/` - local schema contracts for generated entry shapes
- `generated/` - committed derived routing surfaces
- `tests/` - unit and integration coverage for build and validate flows

## Build and validate

Install local dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Build the routing surfaces from sibling AoA repositories:

```bash
python scripts/build_router.py
```

Validate the generated outputs:

```bash
python scripts/validate_router.py
```

Run tests:

```bash
pytest
```

The builder defaults to sibling repository roots:

- `../aoa-techniques`
- `../aoa-skills`
- `../aoa-evals`
- `../aoa-memo`

Override them when needed:

```bash
python scripts/build_router.py --techniques-root ../custom-techniques --generated-dir ./generated
```

## Deferred in v0.1

These are intentionally out of scope for the first foundation release:

- pairings
- tiny-model entrypoints
- same-kind relation graphs
- memo recall surfaces
- broader KAG and graph views

## Intended role

`aoa-routing` should act as a small, deterministic bridge:

- models ask which surface kind they need
- routing points them to the smallest next object
- meaning stays in the source repositories
