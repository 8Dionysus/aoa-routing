# Agon Mechanic Guidance

Agon in `aoa-routing` is routing-owned and pre-protocol only. It names gate
candidates, owner-review handoffs, and recurrence observations; it does not
open arenas, issue verdicts, write scars, schedule retention, mutate rank, or
promote Tree-of-Sophia source truth.

Use active parts first:

- `parts/gate-routing/` owns gate trigger contracts, route hints, owner dispatch
  seam payloads, generated registry, builder, validator, and tests.
- `parts/recurrence-adapter/` owns the observation-only recurrence manifest for
  Agon gate surfaces.

Current Agon follow-through quest records, if opened, live in root
`quests/agon/` with current repo-qualified IDs. Historical receipts live in
`legacy/raw/`.

Enter `legacy/` only through `PROVENANCE.md` for old-path accounting or raw
historical receipts.
