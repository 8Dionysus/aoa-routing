# Decision Records Index

This directory is the durable decision surface for `aoa-routing`.

Use it when a future contributor needs the rationale for a routing route, topology, owner boundary, generated-output policy, validator route, source-lane handoff, fallback posture, or optional routing seam.

Ordinary implementation notes, generated output, runtime logs, private evidence, proof verdicts, route examples, and one-off planning thoughts route to their owning surfaces instead.

## Operating Card

| Field | Route |
| --- | --- |
| role | durable routing decision rationale entrypoint and index chooser |
| input | changed routing surface, owner handoff, rejected option, validation guard, source-lane split, generated-output policy, or fallback pressure |
| output | canonical decision note, generated lookup indexes, and route back to the owning source surface |
| owner | `docs/decisions/AGENTS.md` for lane law; decision notes for rationale; generated indexes for lookup only |
| next route | owning generated/schema/example/script/test surface first, then nearest route card, `README.md`, `ROADMAP.md`, generated lookup indexes, or the affected sibling owner |
| validation | executable decision-lane checks in `docs/decisions/AGENTS.md`, plus the owning validator for the changed surface |

## Authority

Decision notes explain why a route was chosen.

They are weaker than the source surface they describe:

- generated routing outputs stay in `generated/`;
- core schema contracts stay in `routing/core/schemas/`;
- mechanic-owned contracts stay under their owning `mechanics/<head>/parts/<part>/`;
- build and validation behavior stays in `scripts/`;
- regression proof stays in `tests/`;
- route direction stays in `README.md` and `ROADMAP.md`;
- source repositories keep stronger truth for technique, skill, eval, memory, role, playbook, KAG, stats, center, runtime, and ToS meaning.

Generated decision indexes are weaker than the decision notes. They exist to make lookup cheaper for agents, not to carry decision rationale.

## Index Shape

Each decision owns:

- a canonical `Decision ID: AOA-RT-D-####`;
- a full canonical-ID filename, for example `AOA-RT-D-0001-*.md`;
- an `## Index Metadata` block naming original date, surface classes, routing surfaces, source lanes, guard families, and posture.

The lookup indexes under [indexes](indexes/README.md) are generated from that metadata:

- [Decisions by canonical ID and number](indexes/by-number.md)
- [Decisions by date](indexes/by-date.md)
- [Decisions by surface class](indexes/by-surface.md)
- [Decisions by routing surface](indexes/by-routing-surface.md)
- [Decisions by source lane](indexes/by-source-lane.md)
- [Decisions by validation or guard family](indexes/by-guard.md)

After decision metadata changes, use the generation and parity route in
`docs/decisions/AGENTS.md`; generated indexes remain builder-owned.

## Lookup Route

Do not hand-maintain a "latest decision" roster in this README. That list drifts as soon as a new decision lands.

Use the generated indexes instead:

- [by number](indexes/by-number.md) for the complete canonical ledger;
- [by date](indexes/by-date.md) for recent landings;
- [by surface](indexes/by-surface.md), [by routing surface](indexes/by-routing-surface.md), and [by source lane](indexes/by-source-lane.md) for route-pressure lookup;
- [by guard](indexes/by-guard.md) for validation, owner-boundary, generated-output, source-authority, or fallback pressure.

The first decision records why this lane exists without turning it into generated routing authority.

## Addressing

Full canonical-ID decision paths are the active source files:

- `docs/decisions/AOA-RT-D-0001-*.md`
- `docs/decisions/AOA-RT-D-0002-*.md`
- `docs/decisions/AOA-RT-D-####-*.md`

Canonical IDs remain stable handles. Previous path names belong to git, PR, or release history, not to a compatibility lookup layer.

## Naming

Use the full canonical decision ID as the filename prefix:

`AOA-RT-D-0001-short-decision-slug.md`

Prefer short titles that name the route, not the whole debate.

## Template

Start from [TEMPLATE.md](TEMPLATE.md) for new decisions. Keep notes concise, but include enough context, options, rationale, consequences, source surfaces, and validation for a future agent to avoid repeating the same route question.
