# Stage Producer Succession To aoa-sdk

## Index Metadata

- Decision ID: AOA-RT-D-0004
- Original date: 2026-07-23
- Surface classes: ownership/succession, route-law, compatibility, repository lifecycle
- Routing surfaces: thin router, generated outputs, routing source-home, release contour
- Source lanes: routing, aoa-sdk, sibling owners, runtime owner
- Guard families: source-owned authority, ABI preservation, shadow parity, rollback, consumer-zero, operator approval
- Posture: accepted

## Context

The R0 succession baseline established that `aoa-routing` is the one canonical
and runnable routing producer, while `aoa-sdk` is a typed consumer. The
producer reads fourteen sibling repositories and emits fourteen root
compatibility outputs. The two repositories maintain separate control-plane,
validation, release, KAG, and consumer coordination surfaces.

The same baseline found that the live runtime mirror was stale, its declared
sync contract still required former flat paths, and its health endpoint did
not verify artifact identity or source provenance. The exact current routing
source ref was also not admitted by the stronger host artifact-trust record.
Those findings make an immediate move or archive unsafe. They also show that
permanent repository separation preserves operational cost without protecting
a distinct semantic owner: source organs own object meaning, runtime owns
execution, and routing owns a deterministic control-plane projection.

`AOA-SDK-D-0071` accepts staged producer succession on the successor side.
The predecessor must independently accept the same transition, compatibility,
freeze, rollback, and archive boundaries before an owner switch can occur.

## Decision

Accept staged succession of the routing producer and routing ABI to
`aoa-sdk`.

This record does not switch current authority. `aoa-routing` remains the sole
canonical producer through R2 contract design, R3 migration rehearsal, and M1
SDK shadow parity. Shadow output cannot publish or become a second canonical
source.

The G5 owner-switch receipt may make `aoa-sdk` the sole canonical producer
only after:

- all fourteen public output paths and `aoa_routing_thin_router_v1` have
  byte parity or explicitly permitted semantic parity;
- clean SDK generation works without an `aoa-routing` checkout dependency;
- rollback is reproduced;
- registered consumers and the live runtime mirror accept the SDK output;
- exact SDK source provenance is admitted by the stronger artifact-trust
  owner.

The owner-only switch changes producer ownership and provenance, not public
artifact paths, schema meaning, or ABI epoch. Any incompatible routing change
requires a separate versioned decision and release.

After G5:

- new routing features land only in `aoa-sdk`;
- this repository permits only compatibility, security, rollback, and
  deprecation maintenance;
- its producer cannot publish a competing canonical output;
- its Git history, decisions, releases, and public provenance remain
  available;
- its rollback implementation remains until compatibility exit conditions
  and consumer-zero are proved.

The compatibility window starts at G5 and cannot close before all registered
active consumers are green on SDK output, direct checkout dependencies reach
consumer-zero, clean install/upgrade/downgrade/rollback checks pass, two
consecutive SDK validation cycles run without predecessor generation, the
runtime and trust records identify the SDK source, and no high-severity
compatibility regression remains.

Archive readiness is not archive authority. Archiving
`8Dionysus/aoa-routing` requires a separate exact operator approval after the
consumer-zero and compatibility evidence is presented.

Source organs continue to own agent, skill, capability, scenario, eval,
memory, KAG, stats, and related domain meaning. The selected runtime owner
continues to own activation and model/tool execution. The successor may
correlate those owner-qualified references but does not absorb their
authority.

This decision is paired with `AOA-SDK-D-0071` and the checked target operating
model at
`aoa-sdk:mechanics/boundary-bridge/parts/consumed-surface-posture-gate/evidence/routing-succession-r1-target-operating-model.json`.
Both decisions are required before G5.

## Options Considered

- Keep `aoa-routing` as a permanent producer. Rejected because it preserves
  the extra control-plane, release, synchronization, and agent-context cost
  after the SDK already owns the typed consumer and future lifecycle surface.
- Extract a shared library while both repositories remain publishers.
  Rejected because two runnable publishers with indistinguishable authority
  create a worse ownership boundary.
- Switch immediately and archive the predecessor. Rejected because current
  runtime synchronization, trust admission, parity, rollback, and
  consumer-zero are not proved.
- Transfer the producer function through rehearsal, non-publishing shadow
  parity, an explicit switch receipt, compatibility maintenance, and
  consumer-zero. Accepted because it preserves one canonical producer at
  every stage and keeps rollback observable.

## Rationale

The selected path preserves the thin-router law while changing its repository
home. `aoa-sdk` can own the routing ABI as a control-plane contract without
becoming the owner of the objects it routes, the policy authority that grants
approval, the runtime body that executes work, the proof owner that evaluates
it, or the memory owner that retains it.

Function-first migration avoids copying this repository's full source-home,
mechanics, quest, KAG, and historical topology into the SDK. Shadow parity
proves the compatibility contract before authority changes. The explicit
receipt and retained rollback route prevent an accepted target note from
silently becoming live runtime truth.

After succession, one repository can own routing implementation, typed public
contracts, compatibility, release, and future
`RouteIntent -> RouteDecision -> RouteExplanation -> RunPlan` integration.
The expected cost reduction must still be measured; repository consolidation
alone is not proof.

## Consequences

- Current generated outputs, schemas, builders, validators, and releases
  remain authoritative until G5.
- R2 may design successor contracts but must not mutate this producer.
- R3 and M1 may use a disposable rehearsal and SDK shadow implementation; they
  may not publish from the SDK.
- The predecessor source-home remains active until G5 and becomes
  maintenance-only afterward.
- The fourteen output paths and ABI epoch remain compatibility surfaces.
- New feature work after G5 is rejected here and routed to `aoa-sdk`.
- Rollback remains operational until its explicit retirement conditions pass.
- Historical surfaces are preserved as history rather than copied as active
  successor scaffolding.
- Consumer-zero must include source, CI, release, mirror, runtime, trust, KAG,
  and checkout dependencies, not only Python imports.
- This record does not authorize repository archive, deletion, rename, or
  hidden ABI change.

## Source Surfaces

- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `routing/AGENTS.md`
- `routing/README.md`
- `routing/source_home.manifest.json`
- `routing/core/README.md`
- `generated/`
- `docs/artifact-bundles/thin_router.bundle.json`
- `aoa-sdk:docs/decisions/AOA-SDK-D-0071-staged-routing-producer-succession.md`
- `aoa-sdk:mechanics/boundary-bridge/parts/consumed-surface-posture-gate/docs/routing-succession-r0-baseline.md`
- `aoa-sdk:mechanics/boundary-bridge/parts/consumed-surface-posture-gate/evidence/routing-succession-r1-target-operating-model.json`

## Validation

Run the decision-index checks, source-home and active-name validators,
repository tests, router build parity, and the release gate. This R1 landing
must leave all generated routing outputs unchanged. G5 later requires separate
live runtime, trust, consumer, and rollback evidence.
