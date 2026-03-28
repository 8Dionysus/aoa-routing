# Two-Stage Skill Selection

Wave-9 adds an optional adjacent routing seam for small-model skill selection.

The seam is intentionally split:

- `aoa-skills` publishes compressed, skill-derived tiny-router inputs
- `aoa-routing` owns the stage wiring, shortlist policy, fallback policy, and tool surfaces

The flow is:

`stage 1 preselect -> stage 2 decision`

## Stage 1

Stage 1 is a tiny-model preselector.

It reads only:

- `aoa-skills/generated/tiny_router_capsules.min.json`
- `aoa-skills/generated/tiny_router_candidate_bands.json`
- `aoa-skills/generated/tiny_router_skill_signals.json`

It may:

- score candidate bands
- score skill cues
- return a shortlist of up to `top_k`
- emit a precision-first confidence reading for the current shortlist
- keep fallback candidates visible out of band when the live shortlist is empty or weak
- mark explicit-only skills as manual

It must not:

- read full skill bodies
- activate a skill
- override source-owned invocation posture

## Stage 2

Stage 2 is the main-model decision step.

It reads only the shortlisted candidates plus the bounded source-owned activation surfaces:

- `aoa-skills/generated/skill_capsules.json`
- `aoa-skills/generated/local_adapter_manifest.json`
- `aoa-skills/generated/context_retention_manifest.json`

It may return only:

- `activate-candidate`
- `manual-invocation-required`
- `no-skill`

Explicit-only skills may rank highly in stage 1, but stage 2 must still require an explicit handle.
Weak or empty shortlists must stay `no-skill`.

## Precision-First Posture

The current router posture is precision-first.

- stage 1 may publish fallback candidates for visibility, but they do not become the live shortlist
- stage 2 should prefer `no-skill` over a weak activation
- the flat routing path remains the default escape hatch when the shortlist signal is weak

## Boundary

This seam is additive.

The current flat routing path remains valid.
Wave-9 does not replace `generated/tiny_model_entrypoints.json` or the existing inspect/expand/pair/recall path.

Routing still owns navigation only.
Skill meaning, trigger wording, and invocation posture stay in `aoa-skills`.
