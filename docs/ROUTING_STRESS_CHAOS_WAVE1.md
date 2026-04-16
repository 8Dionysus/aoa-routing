# Routing Stress Chaos Wave 1

This wave stays additive.
Do not turn `aoa-routing` into a health oracle or a second playbook canon.

## What belongs here

### timeout and honest degradation posture

Use `stress_navigation_hint_v1` when bounded evidence already says a surface is stressed and the router should suggest a safer next hop.

### retrieval outage honesty

Use `composite_stress_route_hint_v1` when the next hop needs a structured join across:

- owner receipts
- playbook stress lane and re-entry gate
- KAG projection health and regrounding
- stats summaries
- optional memo recovery patterns

### skill collision chaos

Keep the two-stage router precision-first.
The important failures are:

- weak shortlists that still try to activate something
- explicit-only shortlist winners that skip the manual handle
- neighboring skills that ignore the better owning skill

## Source-owned landing

This wave uses two source-owned routing surfaces:

- `config/two_stage_router_precision_cases.jsonl`
- `generated/two_stage_router_eval_cases.jsonl`

The config file is the routing-owned precision lane.
The generated eval surface is the committed readout after the builder joins:

- the `aoa-skills` tiny-router cases
- the routing-owned local precision cases

## Rules to preserve

- weak or empty shortlist -> `no-skill`
- explicit-only shortlist winner -> `manual-invocation-required`
- owner receipts outrank stats and memo
- suppression beats confident fiction when evidence is thin

## Verify

```bash
python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills
python scripts/validate_router.py
python -m pytest -q tests
```
