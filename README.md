# aoa-routing

Thin navigation, typing, and dispatch layer for the public AoA stack.

`aoa-routing` does not author new meaning.
It derives lightweight routing surfaces from sibling AoA repositories so models can
decide what to read next without loading each corpus raw.

The core rule for this repository is:

**Source repos own meaning. Routing repo owns navigation.**

## Scope

`aoa-routing` v0.1 covers:

- `aoa-techniques` as the practice canon
- `aoa-skills` as the execution canon
- `aoa-evals` as the proof canon

`aoa-memo` is reserved as a future `kind`, but v0.1 does not ingest concrete memo objects.

## Current ingestion model

The build is intentionally hybrid:

- `aoa-techniques` is read from `generated/technique_catalog.min.json`
- `aoa-skills` is read from `SKILL.md` frontmatter plus `techniques.yaml`
- `aoa-evals` is read from `EVAL.md` frontmatter plus `eval.yaml`

This keeps v0.1 compatible with the current maturity of the sibling repositories
without turning `aoa-routing` into a second source-of-truth.

Explicit `AOA-T-PENDING-*` technique placeholders are allowed in source manifests.
They remain future-only references and do not produce concrete `recommended_paths`
until the upstream technique exists in `aoa-techniques`.

## Generated outputs

The builder writes these tracked artifacts under `generated/`:

- `cross_repo_registry.min.json` - normalized registry of all routeable objects
- `aoa_router.min.json` - minimal entry routing projection
- `task_to_surface_hints.json` - static dispatch hints by surface kind
- `recommended_paths.min.json` - bounded cross-kind upstream/downstream hops

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

- capsules
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
