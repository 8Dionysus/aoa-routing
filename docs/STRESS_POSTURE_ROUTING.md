# STRESS POSTURE ROUTING

## Goal

Teach `aoa-routing` to change next-hop posture when bounded evidence says a surface is stressed.

The router should become more useful under stress, not more magical.

## Why routing is wave-2 leverage

Routing already owns generated registries, dispatch hints, recommended next hops, and bounded return-navigation posture.

Wave 2 adds one new requirement:

**when stress is real, the router should help an agent reground, slow down, or avoid unsafe widening.**

It still does not own the meaning of the stress event itself.

## Input discipline

Routing should prefer these inputs, in order:

1. source-owned stressor or degradation receipts from owner repos
2. bounded eval warnings or failures tied to the same surface family
3. explicit reviewed manifests that point to the owner evidence
4. optional memo context or stats-derived vectors only as secondary shaping signals

Routing should not derive stress posture from arbitrary raw logs or broad anecdotes.

## Output posture

The cleanest later output is an additive machine-readable hint family such as:

- `generated/stress_navigation_hints.min.json`

If that is awkward, add bounded fields to existing hint families such as:

- `generated/task_to_surface_hints.json`
- `generated/recommended_paths.min.json`
- `generated/return_navigation_hints.min.json`

The current second-wave landing stays contract-only: doctrine, one schema, and one example without changing generated router outputs yet.

## Preferred route postures

Wave 2 uses a small posture vocabulary:

- `reground_first`
- `degrade_preferred`
- `human_review_first`
- `stop_before_mutation`
- `route_around_unhealthy_surface`

These are navigation postures, not source-owned verdicts.

## Precedence rule

When signals disagree, prefer:

1. owner-local receipt evidence
2. explicit eval verdicts on the same family
3. optional stats summaries as tie-breakers
4. memo recall as contextual reminder only

## Suppression rule

When evidence is too thin, publish a suppressed hint rather than a confident fiction.

Preferred suppression states:

- `active`
- `low_evidence`
- `disabled`

## Guardrails

- do not make routing the source of stress meaning
- do not silently blacklist a surface forever
- do not parse arbitrary live logs as a default builder input
- do not turn stress hints into hidden mutation permissions
- do not let memo or stats outrank owner-local evidence

## Acceptance shape

A healthy wave-2 contract landing makes it possible to point to:

- one routing hint schema
- one routing hint example
- one documented precedence rule
- one documented suppression rule
- one bounded path where a stressed surface routes first to source evidence or a reground path instead of a broader action lane
