# Agon Provenance

Agon gate-routing was formerly spread across root `docs/`, `config/`,
`schemas/`, `examples/`, `generated/`, `scripts/`, `tests/`, `quests/`, and
`manifests/recurrence/` districts.

The active behavior payload now lives under `mechanics/agon/parts/<part>/`.
Current Agon follow-through quest records, when opened, live under
`quests/agon/` with current repo-qualified IDs. Historical Agon receipts and
historical landing text live under `legacy/raw/`. Old root paths are preserved
as a lookup map in `legacy/INDEX.md`.

Legacy is not a fallback route. Active validators and tests must read active
part paths, and compatibility root scripts may only launch the active part
scripts.
