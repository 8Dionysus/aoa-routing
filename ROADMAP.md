# aoa-routing Roadmap

`aoa-routing` exists to make the AoA stack usable through small, bounded, agent-friendly surfaces.
It should stay a navigation, typing, dispatch, and adjacency layer rather than becoming a fourth source of meaning.

The governing rule stays unchanged:

**Source repos own meaning. Routing owns navigation.**

## Current Baseline

Already merged:

- `aoa-routing` v0.1 foundation:
  - `generated/aoa_router.min.json`
  - `generated/task_to_surface_hints.json`
  - `generated/recommended_paths.min.json`
  - `generated/cross_repo_registry.min.json`
- Stage 1 routing preparation in the active source repos:
  - `aoa-techniques` as the stable technique-catalog source
  - `aoa-skills` with repo-local skill catalogs
  - `aoa-evals` with repo-local eval catalogs

This gives the stack a working cross-repo router, but it is still early in the larger seed vision for lightweight agent surfaces.

## Roadmap

### Milestone 1: Symmetric catalog ingestion

Make `aoa-routing` consume generated source-repo catalogs symmetrically across active AoA repos:

- `aoa-techniques` from `generated/technique_catalog.min.json`
- `aoa-skills` from `generated/skill_catalog.min.json`
- `aoa-evals` from `generated/eval_catalog.min.json`

Goal:

- remove remaining live markdown parsing from `aoa-routing`
- keep source metadata authority inside the source repos
- make routing depend on stable derived reader surfaces only

### Milestone 2: Capsule-ready routing

Enable the next runtime layer once source repos publish local capsules:

- `generated/technique_capsules.json`
- `generated/skill_capsules.json`
- `generated/eval_capsules.json`

`aoa-routing` should not author capsules itself. Its role is to know that capsules exist, route to the right object kind, and support an agent flow of:

`pick -> inspect -> expand`

### Milestone 3: Section expansion surfaces

Support bounded section-level expansion once source repos publish local section shards:

- `generated/technique_sections.full.json`
- `generated/skill_sections.full.json`
- `generated/eval_sections.full.json`

Goal:

- let small models pull one or two sections instead of full bundles
- keep section scope standardized and predictable
- avoid turning routing into a full-bundle mirror

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

For the current KAG/source-lift family, keep `AOA-T-0019` as the default bundle-level metadata entrypoint and treat `AOA-T-0018`, `AOA-T-0020`, `AOA-T-0021`, and `AOA-T-0022` as the explicit special-case companions.

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
- capsules live beside the objects they describe, inside source repos
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
