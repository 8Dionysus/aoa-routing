# Agon Gate Routing

This part owns the pre-protocol Agon gate-routing surface for `aoa-routing`.

| Field | Value |
| --- | --- |
| Role | Emit thin gate candidates and owner-review handoff signals. |
| Input | `config/agon_gate_routing.config.json` and optional sibling Agon registries. |
| Output | `generated/agon_gate_routing_registry.min.json`. |
| Owner | `aoa-routing` for route hints; `Agents-of-Abyss` for Agon law. |
| Next route | `Agents-of-Abyss`, `aoa-agents`, `aoa-evals`, `aoa-memo`, or ordinary service routes named by the hint. |
| Tools | `scripts/build_agon_gate_routing_registry.py`, `scripts/validate_agon_gate_routing.py`. |
| Verification | gate-routing validator and focused tests through root `AGENTS.md` |

## Payload

- `docs/`: gate routing, trigger model, decision boundary, assistant escalation, and owner handoff contracts.
- `config/`: trigger configuration.
- `schemas/` and `examples/`: registry, route hint, trigger, and owner dispatch seam contracts.
- `generated/`: built registry.
- `tests/`: part-local pytest coverage.
- root `quests/agon/`: current Agon gate-routing follow-through notes when
  opened.
- `../../legacy/raw/`: historical receipts.
