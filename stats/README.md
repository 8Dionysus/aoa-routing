# aoa-routing local stats port

This directory exposes statistical questions whose domain meaning belongs to
`aoa-routing`. It uses the shared `aoa-stats` measurement grammar without
moving navigation meaning or dispatch authority into the central organ.

## Current reference measurement

| Measurement | Question | Reference value |
| --- | --- | --- |
| `aoa-routing/stats-regrounding-owner-first-route-ratio` | What fraction of current stats re-grounding hints send their primary inspect action directly to a non-stats owner? | `19 / 22` at source revision `f182803ecb79f121f049d6c372ace3d52f69abb1` |

The reference packet is a census of `hints[]` in
`generated/stats_regrounding_hints.min.json`. Three generic aggregate hints
remain stats-first because their owner inputs do not name one direct owner;
they stay in the denominator rather than being hidden.

## Authority

The ratio describes routing shape only. It does not measure route quality,
correct owner choice, successful dispatch, proof strength, re-grounding policy,
or owner acceptance. `aoa-stats` may validate and compose the packet without
redefining routing meaning.

## Surfaces

- `port.manifest.json` declares the local question, measurement contract, and
  export.
- `packets/stats-regrounding-owner-first-route-ratio.reference.json` records
  the evidence-linked reference observation.
- `generated/stats_regrounding_hints.min.json` remains the immediate derived
  evidence; its mechanic part, schema, builder, and validator remain stronger.
