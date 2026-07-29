# AGENTS.md

Archive boundary: after `v0.4.0` this subtree is historical. It owns no active
route; send current routing and Agent OS work to `aoa-sdk`. The retained
ownership and placement instructions below describe the pre-archive topology
only and must not be followed as current authority.

`mechanics/checkpoint/` owns aoa-routing participation in the shared Checkpoint
mechanic.

Use this mechanic when routing publishes a bounded navigation surface around a
checkpoint, continuity receipt, reentry review, or checkpoint-carry handoff.

Do not put local router source-home behavior here. That belongs in `routing/`.
Do not put active checkpoint files in root `docs/`, `schemas/`, `examples/`,
or `tests/` after the part has a branch-local home.

`legacy/` records retired flat paths only. Active validators must read from
`parts/`.
