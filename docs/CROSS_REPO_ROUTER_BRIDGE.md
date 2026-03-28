# Cross-Repo Router Bridge

Wave-9 is a cross-repo bridge between `aoa-skills` and `aoa-routing`.

The ownership split is deliberate.

## `aoa-skills` owns

- skill-derived tiny-router signals
- skill band membership
- companion relations exposed as compression hints
- manual-invocation posture
- project-overlay markers
- tiny-router shortlist eval cases

These are derived from source-owned skill meaning and must stay aligned with the live skill canon.

## `aoa-routing` owns

- stage-1 shortlist policy
- stage-1 scoring weights and penalties
- fallback behavior
- repo-family boosts
- stage wiring
- prompt blocks
- tool schemas
- examples and router-side eval cases

These are routing decisions, not skill meaning.

## What the bridge must not do

- `aoa-skills` must not become a second routing authority
- `aoa-routing` must not become a second skill canon
- stage 1 must not activate a skill
- router outputs must not copy full skill bodies or source-owned capsule text

The practical contract is:

- `aoa-skills` publishes bounded compression inputs
- `aoa-routing` consumes them to produce a shortlist and decision packet
- source-owned activation authority remains upstream in `aoa-skills`
