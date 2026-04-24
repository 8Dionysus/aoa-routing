# AGENTS.md

Root route card for `aoa-routing`.

## Purpose

`aoa-routing` is the thin navigation and dispatch layer for AoA.
It derives lightweight routing surfaces that point agents to source-owned objects without copying source corpora into a second canon.
This repository owns navigation, not the meaning of things it routes to.

## Owner lane

This repository owns:

- routing projections, registries, dispatch hints, and recommended paths
- advisory owner-layer shortlist hints and bounded return-navigation seams
- optional two-stage routing policy and tool/prompt surfaces
- local schemas, build scripts, validators, and routing integrity checks

It does not own:

- technique, skill, eval, memory, role, playbook, KAG, stats, or center meaning
- activation authority, semantic truth, or live quest sovereignty

## Start here

1. `README.md`
2. `ROADMAP.md`
3. `generated/aoa_router.min.json`
4. `generated/task_to_surface_hints.json`
5. `generated/owner_layer_shortlist.min.json`
6. `generated/recommended_paths.min.json`
7. affected source catalogs or upstream generated surfaces
8. `docs/AGENTS_ROOT_REFERENCE.md` for preserved full root branches


## AGENTS stack law

- Start with this root card, then follow the nearest nested `AGENTS.md` for every touched path.
- Root guidance owns repository identity, owner boundaries, route choice, and the shortest honest verification path.
- Nested guidance owns local contracts, local risk, exact files, and local checks.
- Authored source surfaces own meaning. Generated, exported, compact, derived, runtime, and adapter surfaces summarize, transport, or support meaning.
- Self-agency, recurrence, quest, progression, checkpoint, or growth language must stay bounded, reviewable, evidence-linked, and reversible.
- Report what changed, what was verified, what was not verified, and where the next agent should resume.

## Route away when

- the task requires authored meaning rather than a route to authored meaning
- a stage-one hint starts acting like activation authority
- routing output begins to look like proof, memory, playbook, or KAG doctrine

## Verify

For routing logic changes:

```bash
python scripts/build_router.py
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python -m pytest -q tests
```

Use Agon, stress, quest, or federation-entry branches from `docs/AGENTS_ROOT_REFERENCE.md` when those surfaces change.

## Report

Name the routing surface, output shape, involved source repos, generated outputs changed, and exactly which checks ran.

## Full reference

`docs/AGENTS_ROOT_REFERENCE.md` preserves the former detailed root guidance for route branches, stage-two checks, and review posture.
