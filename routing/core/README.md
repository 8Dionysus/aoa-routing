# Routing Core

## Role

`routing/core/` preserves the retired predecessor thin-router source contour:

`source catalogs -> derived route registry -> public routing outputs -> bounded next hop`

## Inputs

- sibling generated catalogs and route maps;
- local route contracts and validators;
- public root generated outputs when they remain root-published.

## Outputs

- deterministic thin-router builders and validators;
- public route projections, hints, and recommended paths;
- owner-boundary checks that keep routing weaker than source meaning.

## Preserved Contracts

Historical core public-output schemas remain under `schemas/`:

- `schemas/aoa-router.schema.json`
- `schemas/cross-repo-registry.schema.json`
- `schemas/router-entry.schema.json`
- `schemas/task-to-surface-hints.schema.json`
- `schemas/task-to-tier-hints.schema.json`
- `schemas/recommended-paths.schema.json`
- `schemas/pairing-hints.schema.json`
- `schemas/tiny-model-entrypoints.schema.json`

## Current Owner Split

`aoa-sdk` owns active routing navigation, ABI, generation, maintenance, and
publication. Source repositories own technique, skill, eval, memory, agent,
playbook, KAG, stats, runtime, center, and ToS meaning.

Root `generated/` and this source-home remain historical evidence only. They
must not be used to dispatch active work back into `aoa-routing`.

## Stop-Lines

- no source corpus copying;
- no sibling object meaning;
- no activation authority;
- no unbounded graph traversal;
- no root flat path as implementation home after source-home landing.

## Validation

Use the root validation lane only to reproduce or audit preserved history.
Route every active change to `aoa-sdk`.
