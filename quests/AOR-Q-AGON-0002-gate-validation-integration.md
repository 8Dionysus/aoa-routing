# AOR-Q-AGON-0002: Gate Validation Integration

## Owner

`aoa-routing`

## Goal

Integrate Wave V validation into the repo-local verification contour when owner review is ready.

## Candidate command

```bash
python scripts/validate_agon_gate_routing.py
```

## Acceptance

The command is called by the normal release or validation path without replacing `validate_router.py`.
