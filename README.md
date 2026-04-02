# aoa-routing

`aoa-routing` is the thin navigation, typing, dispatch, and federation-entry orientation layer for the public AoA stack.

It does not author new meaning. It derives lightweight routing surfaces from sibling AoA repositories so models can decide what to read next without loading each corpus raw.

**Source repos own meaning. Routing repo owns navigation.**

The live paths are:

- thin-router runtime path: `pick -> inspect -> expand -> object use -> optional pair -> optional recall`
- federation-entry path: `federation root -> entry card -> source authority -> bounded next hop`
- optional wave-9 path: `tiny preselect -> stage-2 skill decision`

## Start here

Use the shortest route by need:

- core routing surfaces: `generated/aoa_router.min.json`, `generated/task_to_surface_hints.json`, `generated/recommended_paths.min.json`, and `generated/task_to_tier_hints.json`
- federation-entry and return posture: `generated/federation_entrypoints.min.json`, `generated/return_navigation_hints.min.json`, [docs/FEDERATION_ENTRY_ABI.md](docs/FEDERATION_ENTRY_ABI.md), and [docs/RECURRENCE_NAVIGATION_BOUNDARY.md](docs/RECURRENCE_NAVIGATION_BOUNDARY.md)
- small-model and two-stage routing seam: `generated/tiny_model_entrypoints.json`, `generated/two_stage_skill_entrypoints.json`, `generated/two_stage_router_prompt_blocks.json`, `generated/two_stage_router_tool_schemas.json`, `generated/two_stage_router_examples.json`, `generated/two_stage_router_manifest.json`, `generated/two_stage_router_eval_cases.jsonl`, and [docs/TWO_STAGE_SKILL_SELECTION.md](docs/TWO_STAGE_SKILL_SELECTION.md)
- current direction: [ROADMAP](ROADMAP.md)

If the task affects ingestion contracts, inspect the relevant upstream generated catalogs before editing routing logic.

## What `aoa-routing` owns

This repository is the source of truth for:

- routing projections and registries
- dispatch hints and recommended next hops
- bounded pairing and return-navigation hints
- optional two-stage routing policy and tool/prompt surfaces
- local schemas, builders, validators, and routing integrity checks

## What it reads

The build stays thin by reading repo-local generated catalogs and registries from sibling repositories instead of reparsing their live authoring files.

Core inputs include:

- `aoa-techniques/generated/technique_catalog.min.json`
- `aoa-skills/generated/skill_catalog.min.json`
- `aoa-evals/generated/eval_catalog.min.json`
- `aoa-memo/generated/memory_catalog.min.json`
- `aoa-agents/generated/model_tier_registry.json`

The federation-entry seam also reads root or generated entry surfaces from `Agents-of-Abyss`, `Tree-of-Sophia`, `aoa-agents`, `aoa-playbooks`, and `aoa-kag`.

`aoa-routing` no longer parses live `SKILL.md`, `techniques.yaml`, `EVAL.md`, or `eval.yaml`.

## Generated outputs

The tracked outputs under `generated/` are grouped into four families:

- core routing: `cross_repo_registry.min.json`, `aoa_router.min.json`, `task_to_surface_hints.json`, `task_to_tier_hints.json`, and `recommended_paths.min.json`
- pairing, recall, and return posture: `pairing_hints.min.json`, `kag_source_lift_relation_hints.min.json`, and `return_navigation_hints.min.json`
- federation entry: `federation_entrypoints.min.json`
- low-context routing: `tiny_model_entrypoints.json` plus the `two_stage_*` family for the optional wave-9 seam

One adjunct example surface also lives here:

- `generated/quest_board.min.example.json`

That board is validator-checked but it is not emitted by `build_router.py`, not read by production routing, and not treated as live dispatch authority.

## Current contour

Inspect actions point to source-owned capsule surfaces. Expand actions point to source-owned section surfaces. `aoa-routing` tells an agent what to read next; it does not copy the owned payloads into a second canon.

Memo recall also stays bounded. The root recall path remains doctrine-first through `aoa-memo`, while the routing hint surface may expose a parallel object-facing family when upstream object contracts and object surfaces are coherent.

For ToS, `tos-root` now hands off first to a source-owned tiny-entry route inside `Tree-of-Sophia`, then to a ToS-specific `kag_view`, and only then to one bounded `aoa-kag` retrieval adjunct. That improves the handoff without turning routing into ToS authority.

For the KAG/source-lift family, the router stays on direct typed one-hop relations only. No graph traversal or open-ended same-kind exploration is introduced at the routing layer.

## Repository layout

- `scripts/` for builders, validators, and shared helpers
- `schemas/` for local public-output contracts
- `generated/` for committed derived routing surfaces
- `tests/` for unit and integration coverage

## Build and validate

Install local dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Build the routing surfaces:

```bash
python scripts/build_router.py
```

Validate them:

```bash
python scripts/validate_router.py
```

Check rebuild parity:

```bash
python scripts/build_router.py --check
```

Run tests:

```bash
pytest
```

The optional wave-9 seam can also be exercised directly:

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
