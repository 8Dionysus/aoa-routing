# aoa-routing

`aoa-routing` is the thin navigation, typing, dispatch, and federation-entry orientation layer for the public AoA stack.

It does not author new meaning. It derives lightweight routing surfaces from sibling AoA repositories so models can decide what to read next without loading each corpus raw.

**Source repos own meaning. Routing repo owns navigation.**

That statement describes the live `predecessor_canonical` state.
`AOA-RT-D-0004` accepts staged producer succession to `aoa-sdk`, but
`aoa-routing` remains canonical until shadow parity and the explicit G5
owner-switch receipt.

> Current release: `v0.3.0`. See [CHANGELOG](CHANGELOG.md) for release notes.

The current public paths are:

- default thin-router path: `pick -> inspect -> expand -> object use -> optional pair -> optional recall`
- additive federation-entry path: `federation root -> entry card -> source authority -> bounded next hop`
- additive pre-protocol Agon gate path: `service or thin route -> pre-protocol gate candidate -> center review`
- skill capability path: `skill root -> owner catalog -> owner capability graph -> task-local composition`

For the current language-neutral ABI hardening contour, owner-owned federation
capsules must keep low-context route fields on docs, manifests, schemas, or
generated JSON. Repo-local build and validator files remain visible only as
owner-local validation support.
The same low-context posture applies to skills: routing may inspect the compact
owner catalog and point into the owner capability graph, but it does not copy
full capability contracts or construct a second skill-selection authority.

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
- routing-owned statistical questions and evidence-linked reference packets: [stats](stats/README.md)
- Agon gate routing: `mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json`, [mechanics/agon/parts/gate-routing/docs/gate-routing.md](mechanics/agon/parts/gate-routing/docs/gate-routing.md), [mechanics/agon/parts/gate-routing/docs/trigger-model.md](mechanics/agon/parts/gate-routing/docs/trigger-model.md), [mechanics/agon/parts/gate-routing/docs/decision-boundary.md](mechanics/agon/parts/gate-routing/docs/decision-boundary.md), [mechanics/agon/parts/gate-routing/docs/assistant-escalation.md](mechanics/agon/parts/gate-routing/docs/assistant-escalation.md), and [mechanics/agon/parts/gate-routing/docs/owner-handoffs.md](mechanics/agon/parts/gate-routing/docs/owner-handoffs.md)
- skill capability route: `generated/tiny_model_entrypoints.json` plus the
  source-owned `aoa-skills/generated/agent_skill_catalog.min.json` and
  `aoa-skills/generated/capability_graph.json`
- owner capability-routing decision:
  `docs/decisions/AOA-RT-D-0003-owner-capability-routing.md`
- accepted producer-succession decision:
  `docs/decisions/AOA-RT-D-0004-stage-producer-succession-to-aoa-sdk.md`
- durable routing rationale: [docs/decisions](docs/decisions/README.md)
- release-readiness and publication shape: [docs/RELEASING](docs/RELEASING.md)
- current direction: [ROADMAP](ROADMAP.md)

If the task affects ingestion contracts, inspect the relevant upstream generated catalogs before editing routing logic.

## Verify current outputs

Executable build, validation, and test routes are owned by
[AGENTS.md](AGENTS.md#verify) and the nearest nested route card.
`scripts/release_check.py` composes the repository-wide gate; this README
keeps the public surface map rather than a second command catalog.

## Route by need

- core routing registries and cross-repo bridge: `generated/cross_repo_registry.min.json`, `generated/aoa_router.min.json`, `generated/task_to_surface_hints.json`, `generated/task_to_tier_hints.json`, `generated/recommended_paths.min.json`, and [mechanics/boundary-bridge/parts/cross-repo-router-bridge/docs/cross-repo-router-bridge](mechanics/boundary-bridge/parts/cross-repo-router-bridge/docs/cross-repo-router-bridge.md)
- pairing, recall, and KAG/source-lift hints: `generated/pairing_hints.min.json`, `generated/kag_source_lift_relation_hints.min.json`, and `generated/return_navigation_hints.min.json`
- federation-entry and bounded return surfaces: `generated/federation_entrypoints.min.json`, [mechanics/boundary-bridge/parts/federation-entry/docs/federation-entry-abi](mechanics/boundary-bridge/parts/federation-entry/docs/federation-entry-abi.md), and [mechanics/recurrence/parts/return-navigation/docs/recurrence-navigation-boundary](mechanics/recurrence/parts/return-navigation/docs/recurrence-navigation-boundary.md)
- live-session reentry review contract: [mechanics/checkpoint/parts/live-session-reentry-route-review/docs/live-session-reentry-route-review](mechanics/checkpoint/parts/live-session-reentry-route-review/docs/live-session-reentry-route-review.md), `mechanics/checkpoint/parts/live-session-reentry-route-review/schemas/live-session-reentry-route-review.schema.json`, and `mechanics/checkpoint/parts/live-session-reentry-route-review/examples/live_session_reentry_route_review.example.json`
- low-context skill routing: `generated/tiny_model_entrypoints.json` points to
  the source-owned agent skill catalog for the callable first cut and the
  source-owned capability graph for deeper navigation
- quest-style adjunct seams: `mechanics/questbook/parts/quest-board-seam/generated/quest_board.min.example.json`, `generated/quest_dispatch_hints.min.json`, [mechanics/questbook/parts/quest-board-seam/docs/quest-board-seam](mechanics/questbook/parts/quest-board-seam/docs/quest-board-seam.md), and [mechanics/questbook/parts/quest-routing-seam/docs/quest-routing-seam](mechanics/questbook/parts/quest-routing-seam/docs/quest-routing-seam.md)
- stress-overlay doctrine and contract surfaces: [mechanics/antifragility/parts/stress-routing/docs/stress-posture-routing](mechanics/antifragility/parts/stress-routing/docs/stress-posture-routing.md), [mechanics/antifragility/parts/degraded-route-hints/docs/degraded-route-hints](mechanics/antifragility/parts/degraded-route-hints/docs/degraded-route-hints.md), [mechanics/antifragility/parts/stress-routing/docs/routing-stress-chaos](mechanics/antifragility/parts/stress-routing/docs/routing-stress-chaos.md), `mechanics/antifragility/parts/degraded-route-hints/schemas/stress_navigation_hint_v1.json`, `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.example.json`, `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.timeout-chaos.example.json`, and `mechanics/antifragility/parts/degraded-route-hints/examples/stress_navigation_hint.skill-collision-chaos.example.json`
- via negativa pruning checklist: [mechanics/antifragility/parts/via-negativa/docs/via-negativa-checklist](mechanics/antifragility/parts/via-negativa/docs/via-negativa-checklist.md)
- additive composite stress-route overlays: `generated/composite_stress_route_hints.min.json`, [mechanics/antifragility/parts/composite-stress-routing/docs/playbook-stress-route-consumption](mechanics/antifragility/parts/composite-stress-routing/docs/playbook-stress-route-consumption.md), [mechanics/antifragility/parts/quarantine-routing/docs/kag-quarantine-route-hints](mechanics/antifragility/parts/quarantine-routing/docs/kag-quarantine-route-hints.md), `mechanics/antifragility/parts/composite-stress-routing/schemas/composite_stress_route_hint_v1.json`, `mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.example.json`, and `mechanics/antifragility/parts/composite-stress-routing/examples/composite_stress_route_hint.retrieval-outage-honesty.example.json`
- Agon gate routing surfaces: `mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json`, [gate routing](mechanics/agon/parts/gate-routing/docs/gate-routing.md), [trigger model](mechanics/agon/parts/gate-routing/docs/trigger-model.md), [decision boundary](mechanics/agon/parts/gate-routing/docs/decision-boundary.md), [assistant escalation](mechanics/agon/parts/gate-routing/docs/assistant-escalation.md), `mechanics/agon/parts/gate-routing/schemas/agon-gate-routing-registry.schema.json`, `mechanics/agon/parts/gate-routing/schemas/agon-gate-trigger.schema.json`, `mechanics/agon/parts/gate-routing/schemas/agon-gate-route-hint.schema.json`, and `mechanics/agon/parts/gate-routing/examples/agon_gate_route_hint.example.json`
- local build, schema, decision, and validation path: `routing/core/schemas/`, owning `mechanics/<head>/parts/<part>/schemas/`, [docs/decisions](docs/decisions/README.md), [AGENTS.md](AGENTS.md#verify), and the nearest nested route card

## What `aoa-routing` owns before G5

This repository is the source of truth for:

- routing projections and registries
- dispatch hints and recommended next hops
- advisory owner-layer shortlist hints
- bounded pairing and return-navigation hints
- bounded first-cut routing over owner-provided callable skill bundles
- direct expansion from `skill-root` into the owner capability graph without a routing-local selector
- routing-local measurement meaning under `stats/`, without cross-owner statistical authority
- local schemas, builders, validators, and routing integrity checks

After G5, canonical producer and ABI ownership move to `aoa-sdk`. This
repository becomes maintenance-only for compatibility, security, rollback,
and deprecation. It must not publish a competing canonical output or accept
new routing features.

## What it reads

The build stays thin by reading repo-local generated catalogs and registries from sibling repositories instead of reparsing their live authoring files.

Core inputs include:

- `aoa-techniques/generated/technique_catalog.min.json`
- `aoa-techniques/generated/technique_kind_manifest.min.json`
- `aoa-skills/generated/agent_skill_catalog.min.json`
- `aoa-skills/generated/capability_graph.json`
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
- low-context routing: `tiny_model_entrypoints.json`, with skill inspection and
  expansion delegated to the owner catalog and capability graph

`generated/aoa_router.min.json` carries the stable artifact identity for the
OS Abyss routing readmodel bundle. The bundle manifest lives at
`docs/artifact-bundles/thin_router.bundle.json` and covers ABI, SBOM-lite
subject inventory, and SLSA/in-toto provenance for the generated routing
family.

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
Only owner-cataloged surfaces receive hints: a retired stats surface disappears
from routing rather than becoming a routing-owned compatibility record.
Runtime Closeout and Owner Landing now follow that lifecycle rule alongside
Titan Summon. The generic Object, Repeated Window, and Source Coverage hints
still route consumers toward the receipt feed, while the still-cataloged
Supersession Drop hint retains the landing receipt owner routes it consumes.

Agon gate routing stays additive too. `mechanics/agon/parts/gate-routing/generated/agon_gate_routing_registry.min.json`
may emit pre-protocol gate candidates, missing-context hints, owner-review
hints, and quarantine hints, but it does not open arenas, issue verdicts,
write scars, schedule retention, mutate rank, grant closure or summon
authority, or author center-owned Agon law.

For ToS, `tos-root` now hands off first to a source-owned tiny-entry route inside `Tree-of-Sophia`, then to a ToS-specific `kag_view`, and only then to one bounded `aoa-kag` retrieval adjunct. That improves the handoff without turning routing into ToS authority.

For the KAG/source-lift family, the router stays on direct typed one-hop relations only. No graph traversal or open-ended same-kind exploration is introduced at the routing layer.

Skill routing now stays inside that core: the router selects the callable
bundle layer from the owner catalog, then points deeper questions to the owner
capability graph. Runtime or session code may compose a task-local DAG; the
router does not publish one.

## Repository layout

- `scripts/` for builders, validators, and shared helpers
- `routing/core/schemas/` for core public-output contracts
- `QUESTBOOK.md` and `quests/` for durable routing quest records and their human open-obligation index
- `mechanics/<head>/parts/<part>/` for mechanic-owned docs, schemas, examples, generated companions, scripts, and tests
- `generated/` for committed derived routing surfaces
- `stats/` for routing-owned measurement questions, contracts, and reference packets
- `tests/` for unit and integration coverage

## Build and validate

Use [AGENTS.md](AGENTS.md#verify) for the repository-wide executable route and
the nearest nested `AGENTS.md` for focused generation or validation. Generated
surfaces stay builder-owned; refresh only the family whose source meaning
changed, then run its owner check and the composed release gate.

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
