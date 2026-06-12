# Rollback Routing

Owns rollback and stay-order route signal contracts.

Active payloads:

- `docs/rollback-route-signals.md`
- `docs/auto-rollback-dispatch.md`
- `docs/stay-order-dispatch.md`
- `schemas/rollback_route_signal_v1.json`
- `schemas/rollback_dispatch_v1.json`
- `examples/rollback_route_signal_v1.example.json`
- `examples/rollback_dispatch.example.json`

Rollback routing never performs durable rollback. It routes authority-aware
signals to the owner that can review and act.
