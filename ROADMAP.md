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
- bounded pairing routing:
  - `aoa-routing` publishes route-owned pair hints for technique, skill, and eval flows
- tiny-model entry routing:
  - `aoa-routing` publishes a low-context query grammar and curated starter entrypoints
- memo dispatch readiness:
  - `aoa-routing` exposes mode-indexed router-ready doctrine recall contracts when upstream `aoa-memo` provides them
  - `aoa-routing` may expose a parallel object-facing memo recall family without replacing the doctrine-first root path
- schema-backed public output validation:
  - registry
  - router projection
  - task-to-surface hints
  - recommended paths
  - pairing hints
  - KAG/source-lift relation hints
  - tiny-model entrypoints
  - federation entry ABI

The current runtime path is:

`pick -> inspect -> expand -> object use -> optional pair -> optional recall`

## Current Milestones

### Milestone 4: Bounded adjacency and pairing surfaces

Merged as bounded routing surfaces:

- skill-to-technique bridge hints
- eval pairing hints
- direct relation hints for the KAG/source-lift family
- bounded relation surfaces
- recommended next hops for `pair` and `expand` flows

Non-goal:

- no graph jungle
- no same-kind exploration explosion
- no open-ended KAG layer inside `aoa-routing`

### Milestone 5: Tiny-model entry surfaces

Merged as model-tier-friendly entrypoints for very small models:

- `generated/tiny_model_entrypoints.json`
- stable query grammar for `pick`, `inspect`, `expand`, `pair`, and bounded `recall`
- curated start surfaces for low-context agents, including kind roots and memo recall starters when upstream contracts are router-ready

For the current KAG/source-lift family, keep `AOA-T-0019` as the default bundle-level metadata entrypoint and treat `AOA-T-0018`, `AOA-T-0020`, `AOA-T-0021`, and `AOA-T-0022` as the explicit special-case companions.

Goal:

- make even small models navigate the stack without loading raw corpus prose

### Milestone 6: Memo dispatch readiness

Merged as bounded memo recall dispatch readiness now that `aoa-memo` exposes initialized source-owned memory surfaces.

Wave 1 tiny-model recall activation now routes small models through published memo recall hints rather than hardcoding semantic-only behavior.
Wave 2 parallel memo adoption keeps the root inspect/expand path doctrine-first while allowing `task_to_surface_hints.json` to advertise an optional object-facing recall family when upstream object contracts are complete.
Wave 3 tiny-model recall-family selection keeps doctrine recall as the default starter path while adding explicit `recall_family = memory_objects` queries and starters for the parallel object-facing family.

`aoa-routing` should own:

- request typing for recall flows
- dispatch to memo surfaces
- bounded inspect/expand/recall hints toward memory

It must not own:

- memory truths
- recall policy authority
- shadow copies of memo objects
- graph traversal programs

### Milestone 7: Federation entry ABI

Merged as a separate orientation layer rather than a widening of the thin router core.

This wave adds:

- `generated/federation_entrypoints.min.json`
- explicit `aoa-root` and `tos-root` root cards
- active entry cards for `agent`, `tier`, `playbook`, and `kag_view`
- `federation_queries` and `federation_starters` in `generated/tiny_model_entrypoints.json`
- schema-backed validation that orientation never points authority at route-owned generated surfaces
- a narrow `tos-root -> source-owned ToS tiny-entry route` handoff without activating `tos_node`
- a second live `kag_view` for `Tree-of-Sophia`, while `kag-view-root` stays defaulted to `aoa-techniques`

The federation entry ABI should own:

- bounded entry orientation
- small-model-ready federation starters
- explicit capsule-to-authority handoff cards

It must not own:

- source authority for AoA, ToS, agents, playbooks, or KAG doctrine
- declared-but-inactive entry kinds
- a widened replacement for the current thin router taxonomy
- a separate starter or active kind for the current ToS tiny-entry route

## Boundaries To Preserve

These boundaries come directly from the seed and should remain hard constraints:

- `aoa-routing` does not author doctrine, policy, or object meaning
- capsules and sections live beside the objects they describe, inside source repos
- global transitions and cross-repo dispatch live in `aoa-routing`
- `aoa-memo` should become a memory layer, not a second routing layer
- `aoa-routing` should never duplicate full bundles as a convenience cache
- same-kind pairing must stay family-scoped and one-hop bounded
- tiny-model entrypoints must stay route-local and must not become a second tier registry
- memo recall hints must advertise only router-ready upstream contracts
- object-facing memo recall must remain a parallel family, not a replacement root kind
- tiny-model recall-family selection must stay additive and memo-scoped rather than becoming a second root registry
- federation entry cards must point authority at owning repos rather than `aoa-routing/generated/*`
- the `tos-root` handoff may point to one source-owned ToS tiny-entry route, but that route must stay inside `Tree-of-Sophia`
- the ToS path may hand off from that source-owned route into a ToS-specific derived `kag_view`, but the default KAG starter remains `aoa-techniques`
- declared federation kinds must stay documented but inactive until their contracts are narrower and more stable
- the federation entry ABI must stay additive beside the thin router core instead of replacing it

## Definition Of Success

The roadmap is successful when a small model can follow one of these paths reliably:

`routing -> capsule -> section expand -> object use -> optional pair -> optional recall`

or

`federation root -> entry card -> source authority -> bounded next hop`

Without:

- reading entire repositories raw
- confusing source-of-truth with runtime surfaces
- wandering through unbounded graph traversals
