# Agon Wave V Routing Landing

Wave V lands Agon gate routing in `aoa-routing`.

## Added surfaces

- `docs/AGON_GATE_ROUTING.md`
- `docs/AGON_GATE_TRIGGER_MODEL.md`
- `docs/AGON_GATE_DECISION_BOUNDARY.md`
- `docs/AGON_GATE_ASSISTANT_ESCALATION.md`
- `docs/AGON_GATE_ROUTING_OWNER_HANDOFFS.md`
- `schemas/agon-gate-routing-registry.schema.json`
- `schemas/agon-gate-trigger.schema.json`
- `schemas/agon-gate-route-hint.schema.json`
- `config/agon_gate_routing.seed.json`
- `generated/agon_gate_routing_registry.min.json`
- `scripts/build_agon_gate_routing_registry.py`
- `scripts/validate_agon_gate_routing.py`
- `tests/test_agon_gate_routing.py`

## Verify

```bash
python scripts/build_agon_gate_routing_registry.py --check
python scripts/validate_agon_gate_routing.py
python -m pytest -q tests/test_agon_gate_routing.py
```

## Status

Pre-protocol.

No live arena.
No runtime dispatch.
No verdict.
No scars.
No retention.
No rank mutation.
