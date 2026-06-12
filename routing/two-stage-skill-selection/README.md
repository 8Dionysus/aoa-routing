# Two-Stage Skill Selection

## Role

This route owns the optional routing-local seam:

`tiny skill preselect -> bounded shortlist -> stage-2 skill decision packet`

It is adjacent to the thin router; it is not the source of skill meaning.

## Inputs

- `aoa-skills` generated tiny-router and skill capsule surfaces;
- local shortlist policy and precision cases;
- prompt, tool, example, manifest, and validation contracts for the seam.

## Outputs

- low-context skill entrypoint routing;
- bounded shortlist and decision-packet helpers;
- prompt/tool contracts that point back to source-owned skill surfaces.

## Stronger Owner Split

`aoa-skills` owns skill source text, invocation posture, adapters, context
contracts, and activation authority. This route owns only preselection and
decision-routing support.

## Stop-Lines

- no copied skill canon;
- no hidden activation;
- no second skill registry;
- no prompt prose that smuggles source-owned payloads.

## Validation

Use `scripts/build_two_stage_skill_router.py --check`,
`scripts/validate_two_stage_skill_router.py`, and
`tests/test_two_stage_skill_router.py` until wrapper localization lands.
