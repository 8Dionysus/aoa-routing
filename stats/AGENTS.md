# AGENTS.md

## Applies to

Everything under `stats/` in `aoa-routing`.

## Role

This directory owns routing-local statistical questions, their embedded
measurement contracts, and evidence-linked reference packets. Shared
statistical grammar and cross-owner composition remain owned by `aoa-stats`.

## Read before editing

1. Root `AGENTS.md` and `README.md`.
2. `stats/README.md` and `stats/port.manifest.json`.
3. The stats re-grounding part contract and generated hint surface.
4. The central measurement and packet contracts under `aoa-stats/stats/`.

## Boundaries

- `port.manifest.json` owns the routing-local question and measurement meaning.
- Reference packets are derived snapshots and remain weaker than the routing
  part contract, schema, builder, validator, and generated hint surface.
- The owner-first ratio describes primary inspect-action shape only. It is not
  route quality, dispatch authority, proof, owner acceptance, or policy.
- Keep packet refs repository-relative and raw owner payloads out of packets.

## Validation

Inspect the owner evidence first:

```bash
jq '{total: (.hints | length), owner_first: ([.hints[] | select(.primary_action.target_repo != "aoa-stats")] | length)}' generated/stats_regrounding_hints.min.json
```

Then validate the port and its referenced packet with the central owner:

```bash
python scripts/validate_local_stats_port.py
```

## Closeout

Report the question or contract changed, the generated owner evidence
inspected, whether the reference packet was refreshed, and which validation
route ran.
