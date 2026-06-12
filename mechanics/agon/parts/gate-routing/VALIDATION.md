# Agon Gate Routing Validation

Run the active checks from the repository root:

```bash
python mechanics/agon/parts/gate-routing/scripts/build_agon_gate_routing_registry.py --check
python mechanics/agon/parts/gate-routing/scripts/validate_agon_gate_routing.py
python -m pytest -q mechanics/agon/parts/gate-routing/tests
```

The root `scripts/build_agon_gate_routing_registry.py` and
`scripts/validate_agon_gate_routing.py` files are compatibility launchers only.
