# AGENTS.md

## Applies to

This card applies to `aoa-routing/kag/` and every nested path until a nearer card
narrows the lane.

## Role

`kag/` preserves the retired local KAG provider packet for `aoa-routing`.
Its compact records describe the historical routing source home and redirect
owner-return consumers to `aoa-sdk`.

## Read before editing

Read the root `AGENTS.md`, this card, `kag/README.md`, `kag/manifest.json`,
`routing/source_home.manifest.json`, and `routing/README.md` before
changing provider records.

## Boundaries

Keep predecessor history with the archived `aoa-routing` source surfaces.
Route active routing meaning and work to `aoa-sdk`. Keep shared KAG schema,
registry, composition, and provider validation with `aoa-kag`; runtime serving
state stays with `abyss-stack` or its named owner.

## Validation

Use the owner validator named in `manifest.json`, then validate the retired
provider through the `aoa-kag` local subtree validator.

## Closeout

Report provider records changed, source-return route changed, owner validation,
`aoa-kag` validation, and the next MCP consumer route.
