# Live-Session Reentry Route Review

## Role

Publish a bounded candidate route-review surface for live-session reentry after
a reviewed checkpoint or continuity artifact.

## Inputs

- checkpoint carry receipt ref from `aoa-memo`;
- continuity route target from `aoa-agents`;
- fallback trace/integrity review target from `aoa-evals`;
- budget authority reference from `Agents-of-Abyss`.

## Outputs

- `docs/live-session-reentry-route-review.md`
- `schemas/live-session-reentry-route-review.schema.json`
- `examples/live_session_reentry_route_review.example.json`
- `tests/test_live_session_reentry_route_review.py`

## Stop-Lines

- no router-owned primary action;
- no direct runtime resume approval;
- no budget policy authorship;
- no continuity truth claim.

## Verification

Use the focused part tests and repo-wide routing validator through root
`AGENTS.md` and the nearest mechanic route card.
