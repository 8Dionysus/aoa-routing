# AGENTS.md

This source-home branch owns routing-local two-stage skill selection support.

Active implementation files stay in this branch:

- `config/` for local policy and precision cases;
- `scripts/` for builder, validator, CLI, and scoring library;
- `schemas/` for the generated two-stage public output contracts;
- `tests/` for part-local behavior coverage;
- `docs/` for the route contract.

Root `scripts/` launchers are compatibility wrappers only. Do not move active
two-stage behavior back to root `config/`, `schemas/`, `docs/`, or `tests/`.

`legacy/` is provenance for former flat paths. It is not an import surface and
must not be used by active validators or builders.

Semantic validation includes `python scripts/validate_semantic_agents.py`.
