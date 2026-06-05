# AGENTS.md

This file applies to durable `aoa-routing` decision rationale under `docs/decisions/`.

## Read First

Before editing decision records here, read:
1. the repository root `AGENTS.md`
2. `README.md`
3. `ROADMAP.md`
4. `docs/AGENTS.md`
5. the generated, schema, example, script, test, config, or upstream source surface the decision describes

## Local Role

`docs/decisions/` is the durable decision-rationale lane for routing boundaries.

Decision notes explain why a route, projection, registry, validator, owner handoff, source-lane split, fallback posture, or generated-surface policy was chosen.
They do not own current routing output, source meaning, activation authority, sibling repo doctrine, schemas, generated payloads, or runtime behavior.

The governing rule still applies:

**Source repos own meaning. Routing repo owns navigation.**

## Authority

Decision notes are weaker than the current source surfaces they describe.

Use this lane to preserve rationale when a future agent would otherwise need to rediscover:

- why a routing surface exists
- why an upstream owner remains authoritative
- why a generated output is bounded or advisory
- why a validator or index exists
- why an option was rejected or deferred

Use owning surfaces for current behavior:

- routing outputs stay in `generated/`
- contracts stay in `schemas/`
- fixtures and public examples stay in `examples/`
- build and validation behavior stays in `scripts/`
- regression proof stays in `tests/`
- source meaning stays in the sibling owner repository named by the route

Generated indexes under `docs/decisions/indexes/` are lookup read models only.
Keep `modeled_surfaces` in `docs/decisions/indexes/index_contract.yaml` as a
top-level list of normalized repo-relative paths under `docs/decisions/`; do
not use it for root non-record Markdown.

## Record Shape

New decision records use:

- canonical filename prefix `AOA-RT-D-####`
- full path shape `docs/decisions/AOA-RT-D-####-short-slug.md`
- an `## Index Metadata` block with `Decision ID`, `Original date`, `Surface classes`, `Routing surfaces`, `Source lanes`, `Guard families`, and `Posture`

Do not renumber existing records. If a decision changes, add a new superseding record and say what it supersedes.

## Hard No

Do not:

- use a decision note to bypass a stronger current contract
- turn decisions into routing output, schema truth, source authority, activation authority, KAG doctrine, memo truth, playbook policy, or center law
- hide generated-output behavior inside a rationale-only note
- copy sibling mechanics, tree, or operator vocabulary when routing needs navigation language
- hand-edit generated indexes

## Validation

After adding or editing decision metadata, run:

```bash
python scripts/generate_decision_indexes.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
```

Also run the owning validator for the generated, schema, example, script, test, config, or upstream route surface the decision describes.
