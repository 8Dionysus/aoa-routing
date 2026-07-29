# aoa-routing Local KAG Provider

`kag/` preserves the retired `aoa-routing` KAG provider packet as portable
source-linked history. Its owner-return route points to `aoa-sdk`; it must not
dispatch active work into this predecessor.

## Operating Card

| Field | Route |
| --- | --- |
| role | retired local KAG provider and successor return route |
| records | `nodes/`, `edges/`, `indexes/`, `projections/`, `receipts/` |
| manifest | `manifest.json` |
| source route | `routing/source_home.manifest.json` and `routing/README.md` |
| consumer route | `aoa-kag` registry/composition, `abyss-stack`, MCP resources |
| owner return | archived `aoa-routing/README.md`, which routes active work to `aoa-sdk` |

## Record Classes

| Class | Preserved record |
| --- | --- |
| node | source surface and owner-return route |
| edge | source surface returns to the owner route |
| index | repository source, entity, artifact, and event indexes |
| projection | MCP-readable source-return packet |
| receipt | validation receipt for the retired packet and successor route |

Git holds compact provider records and source-return handles. Runtime graph,
vector, embedding, cache, and serving state stay with runtime owners.
