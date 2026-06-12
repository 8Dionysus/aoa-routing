# Two-Stage Skill Selection Provenance

## Former Shape

Before the source-home refactor, this seam was split across root districts:

- `config/two_stage_router_policy.json`
- `config/two_stage_router_precision_cases.jsonl`
- `docs/TWO_STAGE_SKILL_SELECTION.md`
- `schemas/two-stage-*.schema.json`
- `scripts/_two_stage_router_lib.py`
- `scripts/build_two_stage_skill_router.py`
- `scripts/two_stage_skill_router.py`
- `scripts/validate_two_stage_skill_router.py`
- `tests/test_two_stage_skill_router.py`

That shape made root districts look like the owner of the two-stage seam.

## Current Shape

The active owner is now this source-home branch:

`routing/two-stage-skill-selection/`

The public generated outputs remain in root `generated/` because federation and
thin-router consumers already read them there.

Root `scripts/` files for this seam are compatibility wrappers only. They route
to the active branch and must not grow independent behavior.

## Legacy Boundary

`legacy/` records former flat addresses and why they stopped being active. It
does not hold active config, schemas, tests, or executable logic.
