# aoa-routing Local KAG Provider

`kag/` exposes the current `aoa-routing` KAG provider packet as portable
source-linked records.

## Operating Card

| Field | Route |
| --- | --- |
| role | local KAG provider for routing source-home, cross-repo registry, and dispatch surface handles |
| records | `nodes/`, `edges/`, `indexes/`, `projections/`, `receipts/` |
| manifest | `manifest.json` |
| source route | `routing/source_home.manifest.json` and `routing/README.md` |
| consumer route | `aoa-kag` registry/composition, `abyss-stack`, MCP resources |
| owner return | `routing/README.md` |

## Record Classes

| Class | Current record |
| --- | --- |
| node | source surface and owner-return route |
| edge | source surface returns to the owner route |
| index | repository source, entity, artifact, and event indexes |
| projection | MCP-readable source-return packet |
| receipt | validation receipt for the current owner route |

Git holds compact provider records and source-return handles. Runtime graph,
vector, embedding, cache, and serving state stay with runtime owners.
