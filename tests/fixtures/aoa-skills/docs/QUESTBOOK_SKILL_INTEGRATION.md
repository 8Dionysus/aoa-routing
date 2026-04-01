# QUESTBOOK integration — aoa-skills

## Purpose

This note shows how `QUESTBOOK.md` fits into `aoa-skills` as the public tracked surface for deferred skill obligations.

## Role split

- skill bundles remain the source of skill meaning
- `generated/public_surface.md`, `generated/governance_backlog.md`, and `generated/skill_evaluation_matrix.md` remain derived readouts
- `QUESTBOOK.md` holds deferred obligations that survive the current bounded diff
- overlay and local-adapter details may trigger quests, but they should not become a hidden second source of truth

## Good anchors in this repo

Use stable anchors such as:
- `docs/RUNTIME_PATH.md`
- `docs/EVALUATION_PATH.md`
- `generated/governance_backlog.md`
- `generated/skill_evaluation_matrix.md`
- `docs/CODEX_PORTABLE_LAYER.md`
- `docs/LOCAL_ADAPTER_CONTRACT.md`
- `docs/OVERLAY_SPEC.md`
- `docs/TWO_STAGE_SKILL_SELECTION.md`

## Initial posture

A skill quest should usually answer one of these:
- which workflow gap survived the current diff
- which proof or evaluation seam drifted
- which runtime export or local adapter contract needs bounded repair
- which repeated overlay exception wants promotion into a real skill or playbook

## Manual-first pilot lane

- `AOA-SK-Q-0002` carried one surviving proof-alignment debt from `aoa-techniques` into the existing derived readouts `generated/governance_backlog.md` and `generated/skill_evaluation_matrix.md`.
- The bounded conclusion for this pass is that those two derived surfaces stay aligned while the remaining proof follow-through belongs in `aoa-evals`, not in a wider skill backlog.
- No ATM10-specific or overlay-specific anchor was introduced for this lane; the repo-local contract stayed inside the existing skill/runtime boundary.
