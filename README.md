# aoa-routing

Thin navigation, typing, dispatch, and federation-entry orientation layer for the public AoA stack.

`aoa-routing` does not author new meaning.
It derives lightweight routing surfaces from sibling AoA repositories so models can
decide what to read next without loading each corpus raw.

The core rule for this repository is:

**Source repos own meaning. Routing repo owns navigation.**

The current thin-router runtime path is:

`pick -> inspect -> expand -> object use -> optional pair -> optional recall`

The new federation-entry path is separate and additive:

`federation root -> entry card -> source authority -> bounded next hop`

Wave-9 adds another separate and additive path for low-context skill selection:

`tiny preselect -> stage-2 skill decision`

## Scope

`aoa-routing` v0.1 covers:

- `aoa-techniques` as the practice canon
- `aoa-skills` as the execution canon
- `aoa-evals` as the proof canon
- `aoa-memo` as a bounded memo and recall routing surface
- `Agents-of-Abyss`, `Tree-of-Sophia`, `aoa-agents`, `aoa-playbooks`, and `aoa-kag` as source inputs for a separate federation entry ABI

## Current ingestion model

The build reads only repo-local generated catalogs and registries:

- `aoa-techniques` from `generated/technique_catalog.min.json`
- `aoa-skills` from `generated/skill_catalog.min.json`
- `aoa-evals` from `generated/eval_catalog.min.json`
- `aoa-memo` from `generated/memory_catalog.min.json` for root memo routing, with optional object-facing recall contracts and surfaces published through `task_to_surface_hints.json`
- `aoa-agents` from `generated/model_tier_registry.json` for task-to-tier dispatch hints only

For the federation entry ABI, the build also reads:

- `Agents-of-Abyss` root docs for `aoa-root`
- `Tree-of-Sophia` root docs for `tos-root`
- `Tree-of-Sophia/examples/tos_tiny_entry_route.example.json` for the current source-owned ToS tiny-entry handoff
- `aoa-agents/generated/agent_registry.min.json`
- `aoa-agents/generated/runtime_seam_bindings.json`
- `aoa-playbooks/generated/playbook_registry.min.json`
- `aoa-kag/generated/federation_spine.min.json`

`aoa-routing` no longer parses live `SKILL.md`, `techniques.yaml`, `EVAL.md`, or `eval.yaml`.
That contract keeps source meaning inside the source repositories while letting routing stay
deterministic and small.

The builder also reads the relation-bearing `aoa-techniques/generated/technique_catalog.json`
(with `generated/technique_catalog.min.json` as a fallback when needed) to emit one additional
bounded navigation surface for the KAG/source-lift family.
That surface uses direct typed relations only and does not change the thin-router contract.

Explicit `AOA-T-PENDING-*` technique placeholders are allowed in source manifests.
They remain future-only references and do not produce concrete `recommended_paths`
until the upstream technique exists in `aoa-techniques`.

## Generated outputs

The builder writes these tracked artifacts under `generated/`:

- `cross_repo_registry.min.json` - normalized registry of all routeable objects
- `aoa_router.min.json` - minimal entry routing projection
- `task_to_surface_hints.json` - dispatch hints by surface kind, including inspect, expand, pair, and bounded recall actions
- `task_to_tier_hints.json` - task-family hints that derive tier IDs and artifact contracts from `aoa-agents/generated/model_tier_registry.json`
- `recommended_paths.min.json` - bounded cross-kind upstream/downstream hops
- `kag_source_lift_relation_hints.min.json` - bounded one-hop direct relation hints for the KAG/source-lift family
- `pairing_hints.min.json` - bounded pair suggestions derived from cross-kind dependencies and family-scoped direct relations
- `federation_entrypoints.min.json` - bounded federation entry ABI with derived root cards, live entry cards, and explicit source authority refs
- `federation_entrypoints.min.json` also keeps the current `tos-root -> source-owned tiny-entry route -> Tree-of-Sophia kag_view` handoff without activating a new federation kind
- `return_navigation_hints.min.json` - bounded re-entry hints that point runtime and agent layers back to source-owned inspect, expand, or recall surfaces after a governed return decision
- `tiny_model_entrypoints.json` - low-context query grammar and curated starters for small-model routing, including kind roots, memo recall entry hints, and a separate federation-entry seam
- `two_stage_skill_entrypoints.json` - optional stage-1 and stage-2 entry ABI for tiny skill preselection
- `two_stage_router_prompt_blocks.json` - router-owned prompt contract for the two-stage seam
- `two_stage_router_tool_schemas.json` - tool schemas for preselect, packet build, and full route
- `two_stage_router_examples.json` - bounded worked examples for the two-stage seam
- `two_stage_router_manifest.json` - inventory and integration metadata for the two-stage seam
- `two_stage_router_eval_cases.jsonl` - router-side shortlist and decision eval cases

For the KAG/source-lift family, `AOA-T-0019` is the default bundle-level metadata entrypoint.
`AOA-T-0018` stays the section specialist, `AOA-T-0020` stays the provenance companion,
`AOA-T-0021` stays the direct relation hint companion, and `AOA-T-0022` stays the caution companion.
The relation-hint and pairing surfaces stay family-scoped to that seam and do not introduce graph traversal,
rationale layers, or open-ended same-kind exploration.

These public outputs are schema-backed and validator-checked.
`aoa-routing` treats them as stable navigation contracts, not ad hoc helper files.

For the federation-entry seam, `aoa-routing` publishes orientation cards only.
Authority stays in the owning repos.
The doctrinal explanation for that boundary lives in `docs/FEDERATION_ENTRY_ABI.md`.
The recurrence-specific routing boundary lives in `docs/RECURRENCE_NAVIGATION_BOUNDARY.md`.
Return guidance stays orientation-only as well: the router may point back to source-owned authority or support surfaces, but it does not classify return semantics or checkpoint meaning.
For ToS specifically, `tos-root` now hands off first to a source-owned tiny-entry route surface inside `Tree-of-Sophia`, then to a ToS-specific KAG view, before the bounded playbook hop.

Inspect actions point to repo-local capsule surfaces:

- `aoa-techniques/generated/technique_capsules.json`
- `aoa-skills/generated/skill_capsules.json`
- `aoa-evals/generated/eval_capsules.json`
- `aoa-memo/generated/memory_catalog.min.json`

`aoa-routing` does not copy capsule text into its own outputs.
It only tells an agent which source-owned surface to inspect next.

Expand actions point to repo-local section surfaces:

- `aoa-techniques/generated/technique_sections.full.json`
- `aoa-skills/generated/skill_sections.full.json`
- `aoa-evals/generated/eval_sections.full.json`
- `aoa-memo/generated/memory_sections.full.json`

`aoa-routing` does not copy section payloads into its own outputs.
It only tells an agent which source-owned section surface to expand next.

For wave-9, `aoa-routing` also consumes the skill-derived tiny-router bridge that `aoa-skills` publishes:

- `aoa-skills/generated/tiny_router_skill_signals.json`
- `aoa-skills/generated/tiny_router_candidate_bands.json`
- `aoa-skills/generated/tiny_router_capsules.min.json`

Those inputs remain source-owned by `aoa-skills`.
Routing owns only the stage policy and the routing-facing seam built on top of them.

Pair actions point to a route-owned bounded surface:

- `aoa-routing/generated/pairing_hints.min.json`

`aoa-routing` keeps pairing to one-hop bounded hints.
It does not widen pair flow into a graph or same-kind exploration layer.

Recall stays bounded.
`aoa-routing` points memo recall requests at source-owned `aoa-memo` contracts and surfaces,
advertises only router-ready recall modes that upstream `aoa-memo` exposes through contract files,
keeps doctrine recall mode-indexed at the top level of the routing hint surface,
may publish mode-indexed `capsule_surfaces_by_mode` so consumers can follow `inspect -> capsule -> expand` without inventing router-owned memo logic,
and may publish an additional parallel object-facing recall family inside the memo recall hint when upstream object contracts and object surfaces are complete and coherent.
The root memo inspect/expand path remains doctrine-first, while tiny-model entrypoints now keep doctrine recall as the default path and may also publish explicit `recall_family = memory_objects` queries and starters for the parallel object-facing family.
It does not own recall policy authority, memory truth, or graph traversal.

If you are editing inside `generated/`, `schemas/`, `scripts/`, or `tests/`, also follow the nested `AGENTS.md` in that directory.

## Repository layout

- `scripts/` - builder, validator, and shared helpers
- `schemas/` - local schema contracts for the public output envelopes, entries, actions, and hops
- `generated/` - committed derived routing surfaces
- `tests/` - unit and integration coverage for build and validate flows

Canonical bounded flows are also covered by walkthrough smokes in `tests/test_route_walkthroughs.py`,
so `pick`, `inspect`, `expand`, `pair`, and memo `recall` stay anchored to live source-owned surfaces.

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

The optional wave-9 seam can also be exercised directly:

```bash
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python scripts/two_stage_skill_router.py route --routing-root . --skills-root ../aoa-skills --task "Make a bounded repository change with a clear verification step and a final report."
```

The validator enforces both:

- schema contracts for all public generated outputs
- integrity checks across registry, router, hints, recommended paths, and source-owned inspect/expand targets
- rebuild parity between committed routing artifacts and the current sibling source catalogs

It also requires the local guidance surfaces at `generated/AGENTS.md`, `schemas/AGENTS.md`, `scripts/AGENTS.md`, and `tests/AGENTS.md` to remain present and aligned with the thin-router boundary.

Run tests:

```bash
pytest
```

The builder defaults to sibling repository roots:

- `../aoa-techniques`
- `../aoa-skills`
- `../aoa-evals`
- `../aoa-memo`
- `../aoa-agents`
- `../Agents-of-Abyss`
- `../aoa-playbooks`
- `../aoa-kag`
- `../Tree-of-Sophia`

Override them when needed:

```bash
python scripts/build_router.py --techniques-root ../custom-techniques --generated-dir ./generated
```

## Deferred in v0.1

These are intentionally out of scope for the first foundation release:

- same-kind relation graphs
- broader KAG and graph views
- making `aoa-routing` the authority surface for federation root, playbook, tier, or ToS entry paths
- activating `tos_node` or adding a separate federation starter for the current ToS tiny-entry route

## Intended role

`aoa-routing` should act as a small, deterministic bridge:

- models ask which surface kind they need
- routing points them to the smallest next object
- meaning stays in the source repositories

Bounded pairing, tiny-model entrypoints, memo recall dispatch, and the federation entry ABI now sit inside that thin-router posture,
while source-owned meaning remains upstream.
The current ToS tiny-entry sync stays inside that same posture: it improves handoff into `Tree-of-Sophia` without widening the live router taxonomy.
The default `kag-view-root` starter still stays anchored to `aoa-techniques`, while `tos-root` now chooses the ToS-specific `kag_view`.
The optional two-stage skill-selection seam follows the same rule: stage-1 shortlist policy lives here, but skill meaning and activation authority stay in `aoa-skills`.
