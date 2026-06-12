# Stats Regrounding Hints

`generated/stats_regrounding_hints.min.json` is an additive routing surface for
stats-derived re-grounding pressure.

It reads the `aoa-stats` summary surface catalog and source coverage summary so
low-context consumers can see when a stats summary should send them back to
stronger owner truth before use.

## Boundary

This surface is advisory only.

It may:

- name the stats surface that carries risk or thin coverage;
- preserve reason codes from the stats-derived trust posture;
- point to owner truth inputs and stats fallback reads.

It must not:

- decide whether an eval claim is supported;
- change `recommended_paths.min.json`;
- replace `owner_layer_shortlist.min.json`;
- make `aoa-stats` a proof or routing authority;
- bypass `aoa-sdk` re-grounding policy.

## Consumer Posture

Use this surface as a next-read guide:

1. inspect the named owner truth input when present;
2. inspect `aoa-stats.summary_surface_catalog.min`;
3. inspect `aoa-stats.source_coverage_summary.min`;
4. let `aoa-sdk` decide whether re-grounding is recommended or required.
