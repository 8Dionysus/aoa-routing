# Playbook Stress Route Consumption

## Core rule

Route from structured playbook stress surfaces, not authored scenario prose.

Use structured playbook lane and re-entry gate surfaces, not live `PLAYBOOK.md` parsing.

## Inputs

The composite stress-route overlay is allowed to read only:

- `aoa-playbooks/examples/playbook_stress_lane.example.json`
- `aoa-playbooks/examples/playbook_reentry_gate.example.json`
- `aoa-stats/generated/stress_recovery_window_summary.min.json`

The router may point at those surfaces. It may not retell or reinterpret the
source playbook canon.

## Boundary

- playbooks still own degraded lane meaning
- playbooks still own re-entry gate meaning
- stats still owns the derived repeated-window read
- routing only assembles the smallest next bounded hop

## What The Overlay May Say

- which structured source-owned playbook surface to inspect next
- whether the current route should stay source-first or degraded-only
- which re-entry gate still blocks broader movement

## What The Overlay Must Not Say

- that routing can reopen blocked actions
- that a derived route hint outranks the playbook gate
- that playbook prose was parsed as authority
- that `recommended_paths.min.json` changed meaning because a stress overlay exists

## Review Posture

If playbook stress artifacts drift, fix the source-owned examples or the router
builder. Do not patch the generated route hint into a second playbook canon.
