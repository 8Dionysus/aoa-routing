# Route Skills Through Owner Capability Contracts

## Index Metadata

- Decision ID: AOA-RT-D-0003
- Original date: 2026-07-16
- Surface classes: routing/ingestion, topology/source-home, generated/readmodel, scripts/validation, tests/integration
- Routing surfaces: thin router, skill capability route, low-context entrypoints, generated outputs
- Source lanes: routing, aoa-skills, aoa-evals, aoa-kag
- Guard families: source-owned authority, context budget, routing collision, typed dependency parity, task-local composition
- Posture: accepted

## Context

The former optional two-stage skill-selection seam was built around a flat
catalog of 57 independently routed skills plus routing-owned shortlist,
prompt, tool, policy, and precision-case surfaces. The current `aoa-skills`
owner contract instead exposes seven callable bundles through
`generated/agent_skill_catalog.min.json` and represents modes, workflows,
guards, tools, adapters, lifecycle, and typed relations in
`generated/capability_graph.json`.

Recreating the old seam over that owner contract would make `aoa-routing`
maintain a second skill selector and a second partial interpretation of the
capability graph. It would also preserve a repository-persistent execution
shape where the accepted architecture requires task-local DAG composition in
the session or runtime.

## Decision

Retire the routing-owned two-stage skill-selection source branch and all six
of its generated output families.

The thin router now performs a bounded first cut over the owner-provided agent
skill catalog. Deeper applicability, mode, relation, compatibility, and
composition discovery routes to the owner-provided capability graph and its
KAG projection. `aoa-routing` may preserve typed identifiers, owner refs,
lifecycle, and trust fields needed for navigation, but it must not copy full
capability contracts or persist task-local execution DAGs.

This decision supersedes the active optional two-stage route described by the
v0.3.0 roadmap and the former `routing/two-stage-skill-selection/` source home.
It does not supersede AOA-RT-D-0001 or AOA-RT-D-0002; it applies their decision
and source-home boundaries to the new owner contract.

## Options Considered

- Keep the 57-skill seam as a compatibility layer. Rejected because its input
  contract no longer represents current owner truth and compatibility would
  keep obsolete routing competition alive.
- Rebuild the same two-stage machinery over the seven bundles. Rejected
  because the host-visible catalog already supplies the bounded first cut and
  the capability graph already supplies the deeper semantic contract.
- Build a new routing-owned capability retriever or graph. Rejected because
  `aoa-skills` owns capability meaning and `aoa-kag` owns indexed retrieval and
  federation.
- Consume the owner catalog and graph directly, leaving execution composition
  task-local. Accepted because it keeps routing thin, minimizes visible
  competition, and preserves owner-qualified provenance.

## Rationale

Manual integration against `aoa-skills@82aeef95` and
`aoa-evals@52c41d6` produced seven skill registry entries, preserved 21 evals
with typed capability dependencies, and emitted only the existing 14 thin
routing outputs. The route rejected a missing skill graph node, a wrong skill
owner, and a capability-ref ordering mismatch. No former two-stage surface was
needed for the successful build.

The first attempt also showed why owner snapshots must coexist coherently: a
current eval catalog paired with an old technique fixture failed on an
unresolved technique dependency. The successful trial used the current
technique owner rather than weakening dependency checks.

A follow-up missing-capability trial exposed a real false green: the router
preserved an eval's typed ref even when the current capability graph no longer
contained the referenced node. The integration now cross-checks every typed
eval ref against the owner graph's identifier, kind, source family path, and
target owner. Manual missing-node and kind-drift cases now stop before output
generation; durable tests retain the same cross-owner currentness invariant.

## Consequences

- `generated/agent_skill_catalog.min.json` is the compact skill inspection
  input and `generated/capability_graph.json` is the deep expansion target.
- Seven callable bundles remain distinct from the graph's modes, workflows,
  guards, tools, adapters, and external owner references.
- Typed eval capability dependencies pass through routing without being
  flattened into skill or technique dependencies.
- `tiny_model_entrypoints.json` keeps one `skill-root` starter and direct
  inspect/expand queries; it has no routing-local adjacent skill handoff.
- The former source branch, launchers, schemas, policy, precision cases,
  generated outputs, fixtures, and active documentation are removed. Git and
  this record preserve history; no compatibility archive is kept active.
- Task-local DAGs remain session/runtime artifacts. Stable repeated execution
  sequences belong to their workflow or playbook owner, not to routing output.

## Source Surfaces

- `scripts/build_router.py`
- `scripts/router_core.py`
- `scripts/validate_router.py`
- `routing/core/schemas/tiny-model-entrypoints.schema.json`
- `routing/source_home.manifest.json`
- `generated/task_to_surface_hints.json`
- `generated/tiny_model_entrypoints.json`
- `aoa-skills:generated/agent_skill_catalog.min.json`
- `aoa-skills:generated/capability_graph.json`
- `aoa-evals:generated/eval_catalog.min.json`

## Validation

Run the decision-index checks, rebuild and validate the router against current
owner snapshots, exercise positive, negative, coexistence, and retired-surface
manual cases, then run the existing repository release gate and KAG family
checks. Structural tests may preserve only the invariants established by those
manual trials.
