# aoa-routing

`aoa-routing` is the thin navigation, typing, dispatch, and federation-entry orientation layer for the public AoA stack.

It does not author new meaning. It derives lightweight routing surfaces from sibling AoA repositories so models can decide what to read next without loading each corpus raw.

**Source repos own meaning. Routing repo owns navigation.**

The current public paths are:

- default thin-router path: `pick -> inspect -> expand -> object use -> optional pair -> optional recall`
- additive federation-entry path: `federation root -> entry card -> source authority -> bounded next hop`
- optional wave-9 path: `tiny preselect -> stage-2 skill decision`

## Start here

Use the shortest route by need:

- current thin-router core: `generated/aoa_router.min.json`, `generated/task_to_surface_hints.json`, `generated/recommended_paths.min.json`, `generated/task_to_tier_hints.json`, and `generated/owner_layer_shortlist.min.json`
  with technique second-cut routing delegated back to `aoa-techniques/generated/technique_kind_manifest.min.json`
- bounded federation-entry and return posture: `generated/federation_entrypoints.min.json`, `generated/return_navigation_hints.min.json`, [docs/FEDERATION_ENTRY_ABI.md](docs/FEDERATION_ENTRY_ABI.md), and [docs/RECURRENCE_NAVIGATION_BOUNDARY.md](docs/RECURRENCE_NAVIGATION_BOUNDARY.md)
- additive stress-routing contract surfaces: [docs/STRESS_POSTURE_ROUTING.md](docs/STRESS_POSTURE_ROUTING.md), [docs/DEGRADED_ROUTE_HINTS.md](docs/DEGRADED_ROUTE_HINTS.md), `schemas/stress_navigation_hint_v1.json`, and `examples/stress_navigation_hint.example.json`
- additive composite stress-route family: `generated/composite_stress_route_hints.min.json`, [docs/PLAYBOOK_STRESS_ROUTE_CONSUMPTION.md](docs/PLAYBOOK_STRESS_ROUTE_CONSUMPTION.md), [docs/KAG_QUARANTINE_ROUTE_HINTS.md](docs/KAG_QUARANTINE_ROUTE_HINTS.md), `schemas/composite_stress_route_hint_v1.json`, and `examples/composite_stress_route_hint.example.json`
- optional wave-9 seam: `generated/tiny_model_entrypoints.json`, `generated/two_stage_skill_entrypoints.json`, `generated/two_stage_router_prompt_blocks.json`, `generated/two_stage_router_tool_schemas.json`, `generated/two_stage_router_examples.json`, `generated/two_stage_router_manifest.json`, `generated/two_stage_router_eval_cases.jsonl`, and [docs/TWO_STAGE_SKILL_SELECTION.md](docs/TWO_STAGE_SKILL_SELECTION.md)
- current direction: [ROADMAP](ROADMAP.md)

If the task affects ingestion contracts, inspect the relevant upstream generated catalogs before editing routing logic.

## Verify current outputs

Use this order for the current promoted routing contour:

1. `python scripts/validate_router.py`
2. `python scripts/build_router.py --check`
3. `python -m pytest -q tests`
4. `python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check`
5. `python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills`

## Route by need

- core routing registries and cross-repo bridge: `generated/cross_repo_registry.min.json`, `generated/aoa_router.min.json`, `generated/task_to_surface_hints.json`, `generated/task_to_tier_hints.json`, `generated/recommended_paths.min.json`, `generated/owner_layer_shortlist.min.json`, and [docs/CROSS_REPO_ROUTER_BRIDGE](docs/CROSS_REPO_ROUTER_BRIDGE.md)
- pairing, recall, and KAG/source-lift hints: `generated/pairing_hints.min.json`, `generated/kag_source_lift_relation_hints.min.json`, and `generated/return_navigation_hints.min.json`
- federation-entry and bounded return surfaces: `generated/federation_entrypoints.min.json`, [docs/FEDERATION_ENTRY_ABI](docs/FEDERATION_ENTRY_ABI.md), and [docs/RECURRENCE_NAVIGATION_BOUNDARY](docs/RECURRENCE_NAVIGATION_BOUNDARY.md)
- low-context and two-stage routing surfaces: `generated/tiny_model_entrypoints.json`, `generated/two_stage_skill_entrypoints.json`, `generated/two_stage_router_prompt_blocks.json`, `generated/two_stage_router_tool_schemas.json`, `generated/two_stage_router_examples.json`, `generated/two_stage_router_manifest.json`, `generated/two_stage_router_eval_cases.jsonl`, and [docs/TWO_STAGE_SKILL_SELECTION](docs/TWO_STAGE_SKILL_SELECTION.md)
- quest-style adjunct seams: `generated/quest_board.min.example.json`, `generated/quest_dispatch_hints.min.json`, [docs/QUEST_BOARD_SEAM](docs/QUEST_BOARD_SEAM.md), and [docs/QUEST_ROUTING_SEAM](docs/QUEST_ROUTING_SEAM.md)
- stress-overlay doctrine and contract surfaces: [docs/STRESS_POSTURE_ROUTING](docs/STRESS_POSTURE_ROUTING.md), [docs/DEGRADED_ROUTE_HINTS](docs/DEGRADED_ROUTE_HINTS.md), `schemas/stress_navigation_hint_v1.json`, and `examples/stress_navigation_hint.example.json`
- additive composite stress-route overlays: `generated/composite_stress_route_hints.min.json`, [docs/PLAYBOOK_STRESS_ROUTE_CONSUMPTION](docs/PLAYBOOK_STRESS_ROUTE_CONSUMPTION.md), [docs/KAG_QUARANTINE_ROUTE_HINTS](docs/KAG_QUARANTINE_ROUTE_HINTS.md), `schemas/composite_stress_route_hint_v1.json`, and `examples/composite_stress_route_hint.example.json`
- local build, schema, and validation path: `schemas/`, `python scripts/build_router.py`, `python scripts/build_router.py --check`, `python scripts/validate_router.py`, `python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check`, `python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills`, and `python -m pytest -q tests`

## What `aoa-routing` owns

This repository is the source of truth for:

- routing projections and registries
- dispatch hints and recommended next hops
- advisory owner-layer shortlist hints
- bounded pairing and return-navigation hints
- optional two-stage routing policy and tool/prompt surfaces
- local schemas, builders, validators, and routing integrity checks

## What it reads

The build stays thin by reading repo-local generated catalogs and registries from sibling repositories instead of reparsing their live authoring files.

Core inputs include:

- `aoa-techniques/generated/technique_catalog.min.json`
- `aoa-techniques/generated/technique_kind_manifest.min.json`
- `aoa-skills/generated/skill_catalog.min.json`
- `aoa-evals/generated/eval_catalog.min.json`
- `aoa-memo/generated/memory_catalog.min.json`
- `aoa-stats/generated/stress_recovery_window_summary.min.json`
- `aoa-agents/generated/model_tier_registry.json`

The federation-entry seam also reads root or generated entry surfaces from `Agents-of-Abyss`, `Tree-of-Sophia`, `aoa-agents`, `aoa-playbooks`, and `aoa-kag`.

`aoa-routing` no longer parses live `SKILL.md`, `techniques.yaml`, `EVAL.md`, or `eval.yaml`.

The fourth-wave stress overlay reads structured adjunct surfaces only:

- `aoa-playbooks/examples/playbook_stress_lane.example.json`
- `aoa-playbooks/examples/playbook_reentry_gate.example.json`
- `aoa-kag/examples/projection_health_receipt.example.json`
- `aoa-kag/examples/regrounding_ticket.example.json`
- `aoa-memo/generated/memory_object_catalog.min.json`

## Generated outputs

The tracked outputs under `generated/` are grouped into four families:

- core routing: `cross_repo_registry.min.json`, `aoa_router.min.json`, `task_to_surface_hints.json`, `task_to_tier_hints.json`, `recommended_paths.min.json`, and `owner_layer_shortlist.min.json`
- pairing, recall, and return posture: `pairing_hints.min.json`, `kag_source_lift_relation_hints.min.json`, and `return_navigation_hints.min.json`
- additive stress overlays: `composite_stress_route_hints.min.json`
- federation entry: `federation_entrypoints.min.json`
- low-context routing: `tiny_model_entrypoints.json` plus the `two_stage_*` family for the optional wave-9 seam

One adjunct example surface also lives here:

- `generated/quest_board.min.example.json`

That board is validator-checked but it is not emitted by `build_router.py`, not read by production routing, and not treated as live dispatch authority.

## Current contour

Inspect actions point to source-owned capsule surfaces. Expand actions point to source-owned section surfaces. `aoa-routing` tells an agent what to read next; it does not copy the owned payloads into a second canon.

Memo recall also stays bounded. The root recall path remains doctrine-first through `aoa-memo`, while the routing hint surface may expose a parallel object-facing family when upstream object contracts and object surfaces are coherent.

Second-wave surface detection also stays bounded. `owner_layer_shortlist.min.json`
may advertise advisory owner-layer candidates and ambiguity markers, but it
does not become semantic truth or activation authority for eval, memo,
playbook, agent, technique, or skill meaning.

Inside the technique lane, `task_to_surface_hints.json` now points back to the
source-owned `aoa-techniques/generated/technique_kind_manifest.min.json` for
the bounded `domain -> kind` second cut instead of reclassifying technique
meaning inside `aoa-routing`.

Antifragility wave two also stays bounded. The current landing adds routing
doctrine plus one schema/example contract for stress-aware hints, but it does
not add a new generated authority layer or change router dispatch logic yet.

Antifragility wave four stays additive too. `composite_stress_route_hints.min.json`
consumes the new stats summary plus structured playbook, KAG, and memo surfaces,
but it does not replace `recommended_paths.min.json`, `owner_layer_shortlist.min.json`,
or thin-router dispatch authority.

For ToS, `tos-root` now hands off first to a source-owned tiny-entry route inside `Tree-of-Sophia`, then to a ToS-specific `kag_view`, and only then to one bounded `aoa-kag` retrieval adjunct. That improves the handoff without turning routing into ToS authority.

For the KAG/source-lift family, the router stays on direct typed one-hop relations only. No graph traversal or open-ended same-kind exploration is introduced at the routing layer.

The optional wave-9 seam stays additive beside that core. It may help with small-model skill preselection, but it does not replace the flat thin-router path as the default public route.

## Repository layout

- `scripts/` for builders, validators, and shared helpers
- `schemas/` for local public-output contracts
- `examples/` for additive contract examples and validator-backed fixtures
- `generated/` for committed derived routing surfaces
- `tests/` for unit and integration coverage

## Build and validate

Install local dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

For a read-only current-state verify pass:

```bash
python scripts/validate_router.py
python scripts/build_router.py --check
python -m pytest -q tests
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
```

Refresh the tracked routing surfaces:

```bash
python scripts/build_router.py
```

Validate the refreshed outputs:

```bash
python scripts/validate_router.py
python scripts/build_router.py --check
python -m pytest -q tests
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
```

The optional wave-9 seam can also be refreshed directly when you need a targeted stage-wiring update:

```bash
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python scripts/two_stage_skill_router.py route --routing-root . --skills-root ../aoa-skills --task "Make a bounded repository change with a clear verification step and a final report."
```

## Go elsewhere when...

- you need authored technique, skill, or eval meaning: `aoa-techniques`, `aoa-skills`, or `aoa-evals`
- you need explicit memory objects or recall doctrine: `aoa-memo`
- you need scenario-level composition: `aoa-playbooks`
- you need derived knowledge substrate semantics: `aoa-kag`
- you need the ecosystem center and layer map: `Agents-of-Abyss`

## Deferred in v0.1

These remain intentionally out of scope:

- same-kind relation graphs
- broader graph/KAG views as live routing authority
- making `aoa-routing` the authority surface for federation root, playbook, tier, or ToS entry paths
- activating a separate federation starter for the current ToS tiny-entry route

## License

Apache-2.0
