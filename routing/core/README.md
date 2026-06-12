# Routing Core

## Role

`routing/core/` owns the local thin-router source contour:

`source catalogs -> derived route registry -> public routing outputs -> bounded next hop`

## Inputs

- sibling generated catalogs and route maps;
- local route contracts and validators;
- public root generated outputs when they remain root-published.

## Outputs

- deterministic thin-router builders and validators;
- public route projections, hints, and recommended paths;
- owner-boundary checks that keep routing weaker than source meaning.

## Active Contracts

Core public-output schemas live under `schemas/` inside this source-home:

- `schemas/aoa-router.schema.json`
- `schemas/cross-repo-registry.schema.json`
- `schemas/router-entry.schema.json`
- `schemas/task-to-surface-hints.schema.json`
- `schemas/task-to-tier-hints.schema.json`
- `schemas/recommended-paths.schema.json`
- `schemas/pairing-hints.schema.json`
- `schemas/tiny-model-entrypoints.schema.json`

## Stronger Owner Split

`aoa-routing` owns navigation. Source repositories own technique, skill, eval,
memory, agent, playbook, KAG, stats, runtime, center, and ToS meaning.

Root `generated/` may publish cross-repo routing outputs while this route owns
the local source-home behavior that builds and verifies them.

## Stop-Lines

- no source corpus copying;
- no sibling object meaning;
- no activation authority;
- no unbounded graph traversal;
- no root flat path as implementation home after source-home landing.

## Validation

Use the root validation lane until source-home wrappers are fully localized.
