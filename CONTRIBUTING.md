# Contributing to aoa-routing

Thank you for contributing.

## What belongs here

Good contributions:
- routing projections and dispatch hints
- builder and validator logic for generated routing surfaces
- schemas for public output envelopes and entries
- tests that improve routing determinism or integrity checking
- docs that clarify how routing points to source-owned surfaces

Bad contributions:
- copied source-owned meaning from neighboring repositories
- memory objects, workflow authoring, or eval doctrine
- routing features that behave like a second source of truth
- heavy semantic layers that exceed the thin navigation role of this repository

## Before opening a PR

Please make sure:
- source repositories still own meaning and `aoa-routing` still owns navigation
- inspect and expand targets still point to source-owned surfaces
- output-shape changes are called out explicitly
- generated outputs stay deterministic and bounded
- no copied content quietly replaces source-owned meaning

Run the documented local path before opening a PR:

```bash
python -m pip install -r requirements-dev.txt
python scripts/build_router.py
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python -m pytest -q tests
```

## Preferred PR scope

Prefer:
- 1 routing surface or builder change per PR
- or 1 focused schema or validator improvement
- or 1 focused docs clarification about routing boundaries

## Review criteria

PRs are reviewed for:
- determinism
- schema and integrity correctness
- source-of-truth discipline
- bounded scope
- public safety

## Security

Do not use public issues or pull requests for leaks, credentials, or infrastructure-sensitive details.
Use the process in `SECURITY.md`.
