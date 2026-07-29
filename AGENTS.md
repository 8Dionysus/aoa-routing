# AGENTS.md

Root route card for `aoa-routing`.

## Purpose

`aoa-routing` is the thin navigation and dispatch layer for AoA.
It derives lightweight routing surfaces that point agents to source-owned objects without copying source corpora into a second canon.
This repository owns navigation, not the meaning of things it routes to.

`AOA-RT-D-0004` governs the completed producer succession to `aoa-sdk`.
The exact G5 receipt and consumer-zero evidence are SDK-owned. The predecessor
compatibility window and operational rollback role are retired at the final
`v0.4.0` archive boundary. This repository preserves historical source and ABI
evidence only. All routing features, fixes, producer changes, publication
logic, and Agent OS control-plane work route to `aoa-sdk`.

## Owner lane

This repository owns no active routing or maintenance lane after `v0.4.0`.
Its retained contents are historical evidence for:

- the predecessor v1 routing ABI and implementation
- the completed producer-succession and compatibility-exit sequence
- prior releases, decisions, validation contracts, and deprecation notices

It does not own:

- technique, skill, eval, memory, role, playbook, KAG, stats, or center meaning
- activation authority, semantic truth, or live quest sovereignty
- current routing maintenance, release, or archive authority; the final GitHub
  archive action was separately authorized for repository ID `1186624390`

## Start here

1. `README.md`
2. `ROADMAP.md`
3. `generated/aoa_router.min.json`
4. `generated/task_to_surface_hints.json`
5. `generated/owner_layer_shortlist.min.json`
6. `generated/recommended_paths.min.json`
7. affected source catalogs or upstream generated surfaces
8. `stats/README.md` when routing-owned statistical questions or reference packets change
9. `docs/decisions/README.md` when durable route, boundary, generated-output, validator, or source-lane rationale is in scope
10. `docs/decisions/AOA-RT-D-0004-stage-producer-succession-to-aoa-sdk.md`
    when work may affect producer ownership, compatibility, freeze, or archive posture
11. `mechanics/release-support/parts/release-gate-routing/evidence/routing-succession-m3-maintenance-only.json`
    for the historical pre-archive ownership and rollback posture
12. `docs/AGENTS_ROOT_REFERENCE.md` for preserved full root branches


## AGENTS stack law

- Start with this root card, then follow the nearest nested `AGENTS.md` for every touched path.
- Root guidance owns repository identity, owner boundaries, route choice, and the shortest honest verification path.
- Nested guidance owns local contracts, local risk, exact files, and local checks.
- Authored source surfaces own meaning. Generated, exported, compact, derived, runtime, and adapter surfaces summarize, transport, or support meaning.
- Self-agency, recurrence, quest, progression, checkpoint, or growth language must stay bounded, reviewable, evidence-linked, and reversible.
- Report what changed, what was verified, what was not verified, and where the next agent should resume.

## Memory route

For recall, continuity, compaction recovery, comparison with past work, or
preserved lessons, start with `aoa-memo` and the workspace memory map. Session
grounding routes through `.aoa`; local candidate writing routes through this
repository's `memo/` port when that port exists; durable reviewed memory lands
through `aoa-memo`.

## Route away when

- the task requires authored meaning rather than a route to authored meaning
- a stage-one hint starts acting like activation authority
- routing output begins to look like proof, memory, playbook, or KAG doctrine

## GitHub landing workflow

Root `AGENTS.md` owns the repository-wide branch, PR, CI, and merge route.
`.github/AGENTS.md` owns the GitHub-native files that support it.

When the user asks to commit, push, and merge in this repository, use this route:

1. Start from a branch based on the current `origin/main`. If the worktree is already dirty, inventory it first and carry forward only the intended diff.
2. Commit the intended change with a message that names the changed surface.
3. Push the branch and open a pull request that states changed surfaces, validation run, skipped checks, and remaining risk.
4. Wait for GitHub `Repo Validation` and any required GitHub checks. If a check fails, fix the branch and wait for the new result.
5. Merge through GitHub after green validation. Use squash unless repository settings report a different required method; report the method that landed.
6. Return to `main`, fast-forward from `origin/main`, and confirm the worktree is clean before closeout.

If GitHub status or merge permissions cannot be observed, stop the landing route and report the exact blocker instead of guessing.

## Verify

For the final deprecation release:

```bash
python mechanics/release-support/parts/release-gate-routing/scripts/validate_routing_maintenance_only.py
python scripts/validate_active_legacy_names.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python -m pytest -q tests
```

Do not change routing logic here. After `v0.4.0`, route every fix, feature,
producer, generated-output, publication, or Agent OS request to `aoa-sdk`.
Use Agon, stress, quest, or federation-entry branches from `docs/AGENTS_ROOT_REFERENCE.md` when those surfaces change.
Use `docs/decisions/AGENTS.md` when durable routing rationale changes; decision records explain why and do not replace generated routing authority.

## Report

Name the routing surface, output shape, involved source repos, generated outputs changed, and exactly which checks ran.

## Full reference

`docs/AGENTS_ROOT_REFERENCE.md` preserves historical detailed root guidance for route branches and review posture; current skill routing follows AOA-RT-D-0003.
