# aoa-routing Roadmap

`aoa-routing` exists to make the AoA stack usable through small, bounded, agent-friendly surfaces.
It should stay a navigation, typing, dispatch, and adjacency layer rather than becoming a second source of meaning.

The governing rule stays unchanged:

**Source repos own meaning. Routing owns navigation.**

## Current Baseline

Already merged:

- symmetric catalog ingestion across the active source repos:
  - `aoa-techniques` via `generated/technique_catalog.min.json`
  - `aoa-skills` via `generated/skill_catalog.min.json`
  - `aoa-evals` via `generated/eval_catalog.min.json`
- capsule-aware inspect routing:
  - `aoa-routing` points to repo-local capsule surfaces
- section-aware expand routing:
  - `aoa-routing` points to repo-local section surfaces
- schema-backed public output validation:
  - registry
  - router projection
  - task-to-surface hints
  - recommended paths

The current runtime path is:

`pick -> inspect -> expand -> object use`

## Next Waves

### Milestone 4: Bounded adjacency and pairing surfaces

Extend routing with richer, but still bounded, cross-object guidance:

- skill-to-technique bridge hints
- eval pairing hints
- bounded relation surfaces
- recommended next hops for `pair` and `expand` flows

Non-goal:

- no graph jungle
- no same-kind exploration explosion
- no open-ended KAG layer inside `aoa-routing`

### Milestone 5: Tiny-model entry surfaces

Add model-tier-friendly entrypoints for very small models:

- `generated/tiny_model_entrypoints.json`
- stable query grammar for `pick`, `inspect`, `expand`, and `pair`
- curated start surfaces for low-context agents

Goal:

- make even small models navigate the stack without loading raw corpus prose

### Milestone 6: Memo dispatch readiness

Add `memo` as a real routed kind only after `aoa-memo` exists as its own initialized source repo with local memory surfaces.

When that happens, `aoa-routing` should own:

- request typing for recall flows
- dispatch to memo surfaces
- bounded links from techniques, skills, and evals toward memory

It must not own:

- memory truths
- recall policy authority
- shadow copies of memo objects

## Boundaries To Preserve

These boundaries come directly from the seed and should remain hard constraints:

- `aoa-routing` does not author doctrine, policy, or object meaning
- capsules and sections live beside the objects they describe, inside source repos
- global transitions and cross-repo dispatch live in `aoa-routing`
- `aoa-memo` should become a memory layer, not a second routing layer
- `aoa-routing` should never duplicate full bundles as a convenience cache

## Definition Of Success

The roadmap is successful when a small model can follow this path reliably:

`routing -> capsule -> section expand -> object use -> optional pair -> optional recall`

Without:

- reading entire repositories raw
- confusing source-of-truth with runtime surfaces
- wandering through unbounded graph traversals
