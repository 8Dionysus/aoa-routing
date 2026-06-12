# aoa-routing

`aoa-routing` is the thin navigation, typing, dispatch, and federation-entry orientation layer for the public AoA stack.

It does not author new meaning. It derives lightweight routing surfaces from sibling AoA repositories so models can decide what to read next without loading each corpus raw.

**Source repos own meaning. Routing repo owns navigation.**

> Current release: `v0.2.2`. See [CHANGELOG](CHANGELOG.md) for release notes.

The current public paths are:

- default thin-router path: `pick -> inspect -> expand -> object use -> optional pair -> optional recall`
- additive federation-entry path: `federation root -> entry card -> source authority -> bounded next hop`
- additive pre-protocol Agon gate path: `service or thin route -> pre-protocol gate candidate -> center review`
- optional two-stage path: `tiny preselect -> stage-2 skill decision`

For the current language-neutral ABI hardening contour, owner-owned federation
capsules must keep low-context route fields on docs, manifests, schemas, or
generated JSON. Repo-local build and validator files remain visible only as
owner-local validation support.
The same low-context posture now applies to the two-stage prompt and tool
surfaces: they may point to bounded source refs through explicit routing-owned
boundary fields, but their prompt prose and tool descriptions must not copy
source-owned capsule payload fields.

## Start here

Use the shortest route by need:

- current thin-router core: `generated/aoa_router.min.json`, `generated/task_to_surface_hints.json`, `generated/recommended_paths.min.json`, and `generated/task_to_tier_hints.json`
  with technique second-cut routing delegated back to `aoa-techniques/generated/technique_kind_manifest.min.json`
- bounded federation-entry and return posture: `generated/federation_entrypoints.min.json`, `generated/return_navigation_hints.min.json`, [mechanics/boundary-bridge/parts/federation-entry/docs/federation-entry-abi.md](mechanics/boundary-bridge/parts/federation-entry/docs/federation-entry-abi.md), and [mechanics/recurrence/parts/return-navigation/docs/recurrence-navigation-boundary.md](mechanics/recurrence/parts/return-navigation/docs/recurrence-navigation-boundary.md)
- post-W10 live-session reentry review contract: [mechanics/checkpoint/parts/live-session-reentry-route-review/docs/live-session-reentry-route-review.md](mechanics/checkpoint/parts/live-session-reentry-route-review/docs/live-session-reentry-route-review.md), `mechanics/checkpoint/parts/live-session-reentry-route-review/schemas/live-session-reentry-route-review.schema.json`, and `mechanics/checkpoint/parts/live-session-reentry-route-review/examples/live_session_reentry_route_review.example.json`
- Owner route signal / route decision / owner dispatch seam: [mechanics/agon/parts/gate-routing/docs/decision-boundary.md](mechanics/agon/parts/gate-routing/docs/decision-boundary.md), `mechanics/agon/parts/gate-routing/schemas/owner-dispatch-seam.schema.json`, and `mechanics/agon/parts/gate-routing/examples/owner_dispatch_seam.example.json`
- additive stress-routing contract surfaces: [mechanics/antifragility/parts/stress-routing/docs/stress-posture-routing.md](mechanics/antifragility/parts/stress-routing/docs/stress-posture-routing.md), [mechanics/antifragility/parts/degraded-route-hints/docs/degraded-route-hints.md](mechanics/antifragility/parts/degraded-route-hints/docs/degraded-route-hints.md), [mechanics/antifragility/parts/stress-routing/docs/routing-stress-chaos.md](mechanics/antifragility/parts/stress-routing/docs/routing-stress-chaos.md), `mechanics/antifragility/parts/degraded-route-hints/schemas/stress_navigation_hint_v1.json`, `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.example.json`, `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.timeout-chaos.example.json`, and `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.skill-collision-chaos.example.json`
- additive composite stress-route family: `generated/composite_stress_route_hints.min.json`, [mechanics/antifragility/parts/composite-stress-routing/docs/playbook-stress-route-consumption.md](mechanics/antifragility/parts/composite-stress-routing/docs/playbook-stress-route-consumption.md), [mechanics/antifragility/parts/quarantine-routing/docs/kag-quarantine-route-hints.md](mechanics/antifragility/parts/quarantine-routing/docs/kag-quarantine-route-hints.md), `mechanics/antifragility/parts/composite-stress-routing/schemas/composite_stress_route_hint_v1.json`, `mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.example.json`, and `mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.retrieval-outage-honesty.example.json`
- boundary advisory routes: `generated/owner_layer_shortlist.min.json`, `generated/stats_regrounding_hints.min.json`, [mechanics/boundary-bridge/parts/stats-regrounding/docs/stats-regrounding-hints.md](mechanics/boundary-bridge/parts/stats-regrounding/docs/stats-regrounding-hints.md), `mechanics/boundary-bridge/parts/owner-layer-shortlist/schemas/owner-layer-shortlist.schema.json`, `mechanics/boundary-bridge/parts/stats-regrounding/schemas/stats-regrounding-hints.schema.json`, and `mechanics/boundary-bridge/parts/stats-regrounding/examples/stats_regrounding_hint.example.json`
- Agon gate routing: `mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json`, [mechanics/agon/parts/gate-routing/docs/gate-routing.md](mechanics/agon/parts/gate-routing/docs/gate-routing.md), [mechanics/agon/parts/gate-routing/docs/trigger-model.md](mechanics/agon/parts/gate-routing/docs/trigger-model.md), [mechanics/agon/parts/gate-routing/docs/decision-boundary.md](mechanics/agon/parts/gate-routing/docs/decision-boundary.md), [mechanics/agon/parts/gate-routing/docs/assistant-escalation.md](mechanics/agon/parts/gate-routing/docs/assistant-escalation.md), and [mechanics/agon/parts/gate-routing/docs/owner-handoffs.md](mechanics/agon/parts/gate-routing/docs/owner-handoffs.md)
- optional two-stage seam: `generated/tiny_model_entrypoints.json`, `generated/two_stage_skill_entrypoints.json`, `generated/two_stage_router_prompt_blocks.json`, `generated/two_stage_router_tool_schemas.json`, `generated/two_stage_router_examples.json`, `generated/two_stage_router_manifest.json`, `generated/two_stage_router_eval_cases.jsonl`, `routing/two-stage-skill-selection/config/two_stage_router_precision_cases.jsonl`, and [routing/two-stage-skill-selection/docs/two-stage-skill-selection.md](routing/two-stage-skill-selection/docs/two-stage-skill-selection.md)
- durable routing rationale: [docs/decisions](docs/decisions/README.md)
- current direction: [ROADMAP](ROADMAP.md)

If the task affects ingestion contracts, inspect the relevant upstream generated catalogs before editing routing logic.

## Verify current outputs

Use this order for the current promoted routing contour:

1. `python scripts/validate_active_legacy_names.py`
2. `python scripts/validate_router.py`
3. `python scripts/build_router.py --check`
4. `python scripts/generate_decision_indexes.py --check`
5. `python scripts/validate_decision_records.py`
6. `python -m pytest -q tests`
7. `python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check`
8. `python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills`

## Route by need

- core routing registries and cross-repo bridge: `generated/cross_repo_registry.min.json`, `generated/aoa_router.min.json`, `generated/task_to_surface_hints.json`, `generated/task_to_tier_hints.json`, `generated/recommended_paths.min.json`, and [mechanics/boundary-bridge/parts/cross-repo-router-bridge/docs/cross-repo-router-bridge](mechanics/boundary-bridge/parts/cross-repo-router-bridge/docs/cross-repo-router-bridge.md)
- pairing, recall, and KAG/source-lift hints: `generated/pairing_hints.min.json`, `generated/kag_source_lift_relation_hints.min.json`, and `generated/return_navigation_hints.min.json`
- federation-entry and bounded return surfaces: `generated/federation_entrypoints.min.json`, [mechanics/boundary-bridge/parts/federation-entry/docs/federation-entry-abi](mechanics/boundary-bridge/parts/federation-entry/docs/federation-entry-abi.md), and [mechanics/recurrence/parts/return-navigation/docs/recurrence-navigation-boundary](mechanics/recurrence/parts/return-navigation/docs/recurrence-navigation-boundary.md)
- live-session reentry review contract: [mechanics/checkpoint/parts/live-session-reentry-route-review/docs/live-session-reentry-route-review](mechanics/checkpoint/parts/live-session-reentry-route-review/docs/live-session-reentry-route-review.md), `mechanics/checkpoint/parts/live-session-reentry-route-review/schemas/live-session-reentry-route-review.schema.json`, and `mechanics/checkpoint/parts/live-session-reentry-route-review/examples/live_session_reentry_route_review.example.json`
- low-context and two-stage routing surfaces: `generated/tiny_model_entrypoints.json`, `generated/two_stage_skill_entrypoints.json`, `generated/two_stage_router_prompt_blocks.json`, `generated/two_stage_router_tool_schemas.json`, `generated/two_stage_router_examples.json`, `generated/two_stage_router_manifest.json`, `generated/two_stage_router_eval_cases.jsonl`, `routing/two-stage-skill-selection/config/two_stage_router_precision_cases.jsonl`, and [routing/two-stage-skill-selection/docs/two-stage-skill-selection](routing/two-stage-skill-selection/docs/two-stage-skill-selection.md)
- quest-style adjunct seams: `mechanics/questbook/parts/quest-board-seam/generated/quest_board.min.example.json`, `generated/quest_dispatch_hints.min.json`, [mechanics/questbook/parts/quest-board-seam/docs/quest-board-seam](mechanics/questbook/parts/quest-board-seam/docs/quest-board-seam.md), and [mechanics/questbook/parts/quest-routing-seam/docs/quest-routing-seam](mechanics/questbook/parts/quest-routing-seam/docs/quest-routing-seam.md)
- stress-overlay doctrine and contract surfaces: [mechanics/antifragility/parts/stress-routing/docs/stress-posture-routing](mechanics/antifragility/parts/stress-routing/docs/stress-posture-routing.md), [mechanics/antifragility/parts/degraded-route-hints/docs/degraded-route-hints](mechanics/antifragility/parts/degraded-route-hints/docs/degraded-route-hints.md), [mechanics/antifragility/parts/stress-routing/docs/routing-stress-chaos](mechanics/antifragility/parts/stress-routing/docs/routing-stress-chaos.md), `mechanics/antifragility/parts/degraded-route-hints/schemas/stress_navigation_hint_v1.json`, `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.example.json`, `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.timeout-chaos.example.json`, and `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.skill-collision-chaos.example.json`
- via negativa pruning checklist: [mechanics/antifragility/parts/via-negativa/docs/via-negativa-checklist](mechanics/antifragility/parts/via-negativa/docs/via-negativa-checklist.md)
- additive composite stress-route overlays: `generated/composite_stress_route_hints.min.json`, [mechanics/antifragility/parts/composite-stress-routing/docs/playbook-stress-route-consumption](mechanics/antifragility/parts/composite-stress-routing/docs/playbook-stress-route-consumption.md), [mechanics/antifragility/parts/quarantine-routing/docs/kag-quarantine-route-hints](mechanics/antifragility/parts/quarantine-routing/docs/kag-quarantine-route-hints.md), `mechanics/antifragility/parts/composite-stress-routing/schemas/composite_stress_route_hint_v1.json`, `mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.example.json`, and `mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.retrieval-outage-honesty.example.json`
- Agon gate routing surfaces: `mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json`, [gate routing](mechanics/agon/parts/gate-routing/docs/gate-routing.md), [trigger model](mechanics/agon/parts/gate-routing/docs/trigger-model.md), [decision boundary](mechanics/agon/parts/gate-routing/docs/decision-boundary.md), [assistant escalation](mechanics/agon/parts/gate-routing/docs/assistant-escalation.md), `mechanics/agon/parts/gate-routing/schemas/agon-gate-routing-registry.schema.json`, `mechanics/agon/parts/gate-routing/schemas/agon-gate-trigger.schema.json`, `mechanics/agon/parts/gate-routing/schemas/agon-gate-route-hint.schema.json`, and `mechanics/agon/parts/gate-routing/examples/agon_gate_route_hint.example.json`
- local build, schema, decision, and validation path: `routing/core/schemas/`, `routing/two-stage-skill-selection/schemas/`, owning `mechanics/<head>/parts/<part>/schemas/`, [docs/decisions](docs/decisions/README.md), `python scripts/build_router.py`, `python scripts/build_router.py --check`, `python scripts/validate_active_legacy_names.py`, `python scripts/validate_router.py`, `python scripts/generate_decision_indexes.py --check`, `python scripts/validate_decision_records.py`, `python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check`, `python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills`, and `python -m pytest -q tests`

## What `aoa-routing` owns

This repository is the source of truth for:

- routing projections and registries
- dispatch hints and recommended next hops
- advisory owner-layer shortlist hints
- bounded pairing and return-navigation hints
- optional two-stage routing policy and tool/prompt surfaces
- an explicit additive handoff from `skill-root` into the optional two-stage skill seam
- local schemas, builders, validators, and routing integrity checks

## What it reads

The build stays thin by reading repo-local generated catalogs and registries from sibling repositories instead of reparsing their live authoring files.

Core inputs include:

- `aoa-techniques/generated/technique_catalog.min.json`
- `aoa-techniques/generated/technique_kind_manifest.min.json`
- `aoa-skills/generated/skill_catalog.min.json`
- `aoa-evals/generated/eval_catalog.min.json`
- `aoa-memo/generated/memory/memory_catalog.min.json`
- `aoa-stats/generated/stress_recovery_window_summary.min.json`
- `aoa-agents/generated/model_tier_registry.json`

The federation-entry seam also reads root or generated entry surfaces from `Agents-of-Abyss`, `Tree-of-Sophia`, `aoa-agents`, `aoa-playbooks`, and `aoa-kag`.

`aoa-routing` no longer parses live `SKILL.md`, `techniques.yaml`, `EVAL.md`, or `eval.yaml`.

The composite stress overlay reads structured adjunct surfaces only:

- `aoa-playbooks/mechanics/antifragility/parts/stress-lanes/examples/playbook_stress_lane.example.json`
- `aoa-playbooks/mechanics/antifragility/parts/reentry-gates/examples/playbook_reentry_gate.example.json`
- `aoa-kag/examples/projection_health_receipt.example.json`
- `aoa-kag/examples/regrounding_ticket.example.json`
- `aoa-memo/generated/memory-objects/memory_object_catalog.min.json`

## Generated outputs

The tracked outputs under `generated/` are grouped into six families:

- core routing: `cross_repo_registry.min.json`, `aoa_router.min.json`, `task_to_surface_hints.json`, `task_to_tier_hints.json`, and `recommended_paths.min.json`
- boundary advisory: `owner_layer_shortlist.min.json`
- pairing, recall, and return posture: `pairing_hints.min.json`, `kag_source_lift_relation_hints.min.json`, and `return_navigation_hints.min.json`
- additive stress and re-grounding overlays: `composite_stress_route_hints.min.json` and `stats_regrounding_hints.min.json`
- federation entry: `federation_entrypoints.min.json`
- Agon gate routing: `mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json`
- low-context routing: `tiny_model_entrypoints.json` plus the `two_stage_*` family for the optional two-stage seam

One adjunct example surface also lives here:

- `mechanics/questbook/parts/quest-board-seam/generated/quest_board.min.example.json`

That board is validator-checked but it is not emitted by `build_router.py`, not read by production routing, and not treated as live dispatch authority.

## Current contour

Inspect actions point to source-owned capsule surfaces. Expand actions point to source-owned section surfaces. `aoa-routing` tells an agent what to read next; it does not copy the owned payloads into a second canon.

Memo recall also stays bounded. The root recall path remains doctrine-first through `aoa-memo`, while the routing hint surface may expose a parallel object-facing family when upstream object contracts and object surfaces are coherent.
High-pressure memory readiness routing stays owner-first too.
`owner_layer_shortlist.min.json` may point durable-consequence, delta,
retention, or live-ledger pressure to the memo registry and
`aoa-memo/docs/MEMORY_READINESS_BOUNDARY.md`, but that remains a navigation
hint, not proof, KAG policy, a live memory ledger, or routing-owned authority.

Owner-layer surface detection also stays bounded. `owner_layer_shortlist.min.json`
may advertise advisory owner-layer candidates and ambiguity markers, but it
does not become semantic truth or activation authority for eval, memo,
playbook, agent, technique, or skill meaning.

Inside the technique lane, `task_to_surface_hints.json` now points back to the
source-owned `aoa-techniques/generated/technique_kind_manifest.min.json` for
the bounded `domain -> kind` second cut instead of reclassifying technique
meaning inside `aoa-routing`.

Antifragility stress posture also stays bounded. The current landing adds routing
doctrine plus one schema/example contract for stress-aware hints, but it does
not add a new generated authority layer or change router dispatch logic yet.

Antifragility composite stress routing stays additive too. `composite_stress_route_hints.min.json`
consumes the new stats summary plus structured playbook, KAG, and memo surfaces,
but it does not replace `recommended_paths.min.json`, `owner_layer_shortlist.min.json`,
or thin-router dispatch authority.

Stats re-grounding hints are additive in the same way.
`stats_regrounding_hints.min.json` consumes the stats summary surface catalog
and source coverage summary, then points consumers back to owner truth before
they rely on high-risk or thinly grounded stats surfaces. It does not decide
the re-grounding policy itself; that remains an `aoa-sdk` control-plane concern.

Agon gate routing stays additive too. `mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json`
may emit pre-protocol gate candidates, missing-context hints, owner-review
hints, and quarantine hints, but it does not open arenas, issue verdicts,
write scars, schedule retention, mutate rank, grant closure or summon
authority, or author center-owned Agon law.

For ToS, `tos-root` now hands off first to a source-owned tiny-entry route inside `Tree-of-Sophia`, then to a ToS-specific `kag_view`, and only then to one bounded `aoa-kag` retrieval adjunct. That improves the handoff without turning routing into ToS authority.

For the KAG/source-lift family, the router stays on direct typed one-hop relations only. No graph traversal or open-ended same-kind exploration is introduced at the routing layer.

The optional two-stage seam stays additive beside that core. It may help with small-model skill preselection, but it does not replace the flat thin-router path as the default public route.

## Repository layout

- `scripts/` for builders, validators, and shared helpers
- `routing/core/schemas/` for core public-output contracts
- `QUESTBOOK.md` and `quests/` for durable routing quest records and their human open-obligation index
- `mechanics/<head>/parts/<part>/` for mechanic-owned docs, schemas, examples, generated companions, scripts, and tests
- `generated/` for committed derived routing surfaces
- `tests/` for unit and integration coverage

## Build and validate

Install local dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

For a read-only current-state verify pass:

```bash
python scripts/validate_active_legacy_names.py
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
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
python scripts/validate_active_legacy_names.py
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python -m pytest -q tests
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
```

The optional two-stage seam can also be refreshed directly when you need a targeted stage-wiring update:

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
