# Checkpoint Parts

## live-session-reentry-route-review

| Field | Route |
| --- | --- |
| role | publish a bounded candidate review route after a checkpoint or continuity artifact |
| input | reviewed checkpoint receipt ref, budget ref, source-owned primary/secondary/fallback actions |
| output | schema-backed route-review example and validation issues |
| owner | `mechanics/checkpoint/parts/live-session-reentry-route-review/` |
| next route | `aoa-agents` continuity lane, `aoa-memo` writeback/checkpoint carry, or `aoa-evals` trace eval bridge |
| verification | part test plus `validate_live_session_reentry_route_review` in `scripts/validate_router.py` |

This part is candidate-only. It does not approve runtime resume.
