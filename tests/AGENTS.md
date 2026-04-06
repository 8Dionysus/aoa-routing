# AGENTS.md

This file applies to router tests under `tests/`.

## Role of this directory

The test layer keeps `aoa-routing` honest as a thin navigation surface.
Tests here should prove routing integrity without turning the repo into a second content canon.

Important surfaces include:

- `tests/fixtures` for compact sibling-repo fixture roots and route walkthrough data
- `tests/test_build_router.py` for builder behavior
- `tests/test_validate_router.py` for validator behavior
- `tests/test_route_walkthroughs.py` for bounded walkthroughs across pick, inspect, expand, pair, recall, and federation entry paths

## Editing posture

Keep tests explicit and public-safe.
When adding or changing coverage:

- prefer small fixtures over sprawling synthetic corpora
- assert that routing points to source-owned surfaces rather than copied meaning
- keep walkthroughs bounded and deterministic
- make cross-repo assumptions visible in the fixture data
- update tests when schema or output shape changes are intentional

Do not hide real contract changes behind brittle snapshot churn.
A good test should clarify whether the router stayed thin, bounded, and aligned with source-owned surfaces.

## Validation

Run:

```bash
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python -m pytest -q tests
```

If you changed build logic, rebuild the generated surfaces before judging test failures.
