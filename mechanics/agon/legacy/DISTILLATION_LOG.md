# Agon Legacy Distillation Log

## 2026-06-05 Mechanics Refactor

Agon gate-routing moved out of flat root districts into active
`mechanics/agon/parts/` homes.

Distilled into active parts:

- gate-routing docs, config, schemas, examples, generated registry, scripts,
  and tests moved under `parts/gate-routing/`;
- recurrence adapter docs and recurrence manifests moved under
  `parts/recurrence-adapter/`;
- root Agon builder and validator paths became compatibility launchers only;
- former root paths are mapped in `INDEX.md`.

Preserved as legacy:

- `docs/AGON_WAVE5_ROUTING_LANDING.md` remains a raw historical landing note.
- `quests/AOR-Q-AGON-0001-agon-gate-routing.md`,
  `quests/AOR-Q-AGON-0002-gate-validation-integration.md`, and
  `quests/AOR-Q-AGON-0003-routing-to-center-gate-boundary.md` remain raw
  historical quest receipts.

Current route:

- new Agon routing work starts in `parts/gate-routing/`;
- recurrence observation work starts in `parts/recurrence-adapter/`;
- current Agon follow-through quest records, if opened, start in `quests/agon/`
  with current repo-qualified IDs;
- legacy changes account for old paths and raw lineage only.
