# aoa-routing

Thin navigation, typing, and dispatch layer for the public AoA stack.

`aoa-routing` does not author new meaning.
It derives lightweight routing surfaces from sibling AoA repositories so models can
decide what to read next without loading each corpus raw.

The core rule for this repository is:

**Source repos own meaning. Routing repo owns navigation.**

The current runtime path is:

`pick -> inspect -> expand -> object use -> optional pair -> optional recall`

## Scope

`aoa-routing` v0.1 covers:

- `aoa-techniques` as the practice canon
- `aoa-skills` as the execution canon
- `aoa-evals` as the proof canon
- `aoa-memo` as a bounded memo and recall routing surface

## Current ingestion model

The build reads only repo-local generated catalogs and registries:

- `aoa-techniques` from `generated/technique_catalog.min.json`
- `aoa-skills` from `generated/skill_catalog.min.json`
- `aoa-evals` from `generated/eval_catalog.min.json`
- `aoa-memo` from `generated/memory_catalog.min.json`
- `aoa-agents` from `generated/model_tier_registry.json` for task-to-tier dispatch hints only

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
- `tiny_model_entrypoints.json` - low-context query grammar and curated starters for small-model routing, including kind-root starters for low-context entry

For the KAG/source-lift family, `AOA-T-0019` is the default bundle-level metadata entrypoint.
`AOA-T-0018` stays the section specialist, `AOA-T-0020` stays the provenance companion,
`AOA-T-0021` stays the direct relation hint companion, and `AOA-T-0022` stays the caution companion.
The relation-hint and pairing surfaces stay family-scoped to that seam and do not introduce graph traversal,
rationale layers, or open-ended same-kind exploration.

These public outputs are schema-backed and validator-checked.
`aoa-routing` treats them as stable navigation contracts, not ad hoc helper files.

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

Pair actions point to a route-owned bounded surface:

- `aoa-routing/generated/pairing_hints.min.json`

`aoa-routing` keeps pairing to one-hop bounded hints.
It does not widen pair flow into a graph or same-kind exploration layer.

Recall stays bounded.
`aoa-routing` points memo recall requests at source-owned `aoa-memo` contracts and surfaces,
advertises only router-ready recall modes that upstream `aoa-memo` exposes through contract files,
and keeps those contracts mode-indexed in the routing hint surface.
It does not own recall policy authority, memory truth, or graph traversal.

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

The validator enforces both:

- schema contracts for all public generated outputs
- integrity checks across registry, router, hints, recommended paths, and source-owned inspect/expand targets
- rebuild parity between committed routing artifacts and the current sibling source catalogs

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

Override them when needed:

```bash
python scripts/build_router.py --techniques-root ../custom-techniques --generated-dir ./generated
```

## Deferred in v0.1

These are intentionally out of scope for the first foundation release:

- same-kind relation graphs
- broader KAG and graph views

## Intended role

`aoa-routing` should act as a small, deterministic bridge:

- models ask which surface kind they need
- routing points them to the smallest next object
- meaning stays in the source repositories

Bounded pairing, tiny-model entrypoints, and memo recall dispatch now sit inside that thin-router contract,
while source-owned meaning remains upstream.
