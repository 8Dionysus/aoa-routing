# Routing Source Home And Mechanics Topology

## Index Metadata

- Decision ID: AOA-RT-D-0002
- Original date: 2026-06-05
- Surface classes: topology/source-home, mechanics/route-law, scripts/validation, tests/topology
- Routing surfaces: routing source-home, mechanics atlas, thin router, generated outputs
- Source lanes: routing, sibling owners, OS Abyss mechanics
- Guard families: source-home boundary, mechanics topology, legacy provenance, generated-output boundary, owner boundary
- Posture: accepted

## Context

`aoa-routing` had grown as flat root districts: `docs/`, `schemas/`,
`examples/`, `generated/`, `config/`, `scripts/`, `tests/`, `quests/`, and
`manifests/`. That made local routing source behavior, shared OS Abyss mechanic
participation, public generated outputs, validation support, and old-path
accounting look like the same kind of surface.

During the mechanics refactor, durable quest source records and the human
questbook index needed a correction: sibling refactored repositories keep
`QUESTBOOK.md` and `quests/<lane>/<state>/` as source-record surfaces, while
`mechanics/questbook/` owns operation law, validation posture, and generated
reader support. Quest records are not ordinary mechanic part payloads.

Sibling AoA repositories have already separated source homes from mechanics:
source object families stay in their owner homes, while mechanics carry
repeatable operation parts with local payloads, provenance, and legacy
accounting. External implementation references also support the split:
packaging and test guidance warns against flat import/source ambiguity, and
agent guidance favors clear role/input/output/owner/next-route/tool/validation
interfaces over broad prose.

## Decision

Adopt `routing/` as the local source-home district for `aoa-routing` owned
navigation behavior.

Adopt `mechanics/` as the active operation atlas for shared OS Abyss mechanics
where `aoa-routing` owns a functioning routing part. Head mechanic names follow
federation vocabulary. Parts are operation nodes, not file-type buckets.

Root generated outputs may remain root-published only when they are public
cross-repo routing surfaces. Root scripts may remain only as repo-wide
validators, release gates, shared builders, or compatibility wrappers once
implementation moves to source homes or mechanic parts.

Keep root `QUESTBOOK.md` and `quests/` as active source-record surfaces for
routing-local obligations. Use lane/state paths such as
`quests/routing/<state>/AOA-RT-Q-*.yaml`. Future Agon follow-through notes in
`quests/agon/` must use current repo-qualified IDs. Historical Agon receipts
route to `mechanics/agon/legacy/raw/`.
`mechanics/questbook/` owns the operation contract around active records, not
their source-record placement or Agon legacy archive.

Each mechanic package carries its own `ROADMAP.md` for package-local current
contour, future route pressure, condition-based next moves, and stop-lines.
Root `ROADMAP.md` remains the repo-level direction surface.

Former flat paths are historical lookup facts. They route through the owning
`PROVENANCE.md` and `legacy/` index when payloads move.

## Options Considered

- Keep the flat root district layout. This avoids immediate path churn but
  keeps source-home behavior, mechanics payloads, generated outputs, and
  validation support mixed.
- Create `mechanics/routing` as the main parent. This misnames the local router
  as a shared mechanic and hides the difference between source-home behavior
  and OS Abyss mechanic participation.
- Create `routing/` plus shared head mechanics. This matches repo-family
  topology and keeps local routing behavior distinct from Agon, Experience,
  Checkpoint, Recurrence, Questbook, Boundary Bridge, Antifragility, Release
  Support, Titan, and RPG participation.

## Rationale

`aoa-routing` owns navigation, typing, dispatch, route projection, and bounded
next-hop hints. Those are source-home concerns when they are local to the
router.

Agon gate routing, checkpoint reentry review, recurrence return hints,
experience office/service/adoption routing, quest routing, boundary bridges,
stress/rollback routing, release/deployment routes, Titan routes, and RPG
navigation are not local topic buckets. They are routing-owned parts of shared
OS Abyss mechanics and need part-local contracts, payload homes, validation,
and legacy provenance.

The selected topology lets public generated outputs stay discoverable while
moving source behavior and mechanic payloads into their real owners.

## Consequences

Future refactors should move file-name clusters by owner and operation:

- routing-local source behavior to `routing/<route>/`;
- routing-local quest records to `QUESTBOOK.md` and `quests/<lane>/<state>/`;
- shared mechanic payloads to `mechanics/<head>/parts/<part>/`;
- package-local mechanic future contours to `mechanics/<head>/ROADMAP.md`;
- repo-wide validators, release gates, and platform support to root support
  districts;
- old-path lookup to package `PROVENANCE.md` and `legacy/`.

Validators must make the split explicit before broad root cleanup. A path
remaining at root needs an owner reason, not inertia.

## Source Surfaces

- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `QUESTBOOK.md`
- `quests/AGENTS.md`
- `quests/README.md`
- `routing/AGENTS.md`
- `routing/README.md`
- `routing/source_home.manifest.json`
- `mechanics/AGENTS.md`
- `mechanics/README.md`
- `mechanics/topology.json`
- `mechanics/<head>/ROADMAP.md`
- `scripts/validate_source_home.py`
- `scripts/validate_mechanics_topology.py`
- `scripts/validate_active_legacy_names.py`
- `tests/test_source_home_topology.py`
- `tests/test_mechanics_topology.py`
- `tests/test_active_legacy_name_noise.py`
- `https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/`
- `https://pytest.org/en/7.4.x/explanation/goodpractices.html`
- `https://www.anthropic.com/engineering/building-effective-agents?lang=en-US`
- `https://openai.com/index/unrolling-the-codex-agent-loop/`

## Validation

Run:

```bash
python scripts/validate_source_home.py
python scripts/validate_mechanics_topology.py
python scripts/validate_nested_agents.py
python scripts/generate_decision_indexes.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python -m pytest -q tests/test_source_home_topology.py tests/test_mechanics_topology.py tests/test_nested_agents_docs.py tests/test_decision_indexes.py
```
