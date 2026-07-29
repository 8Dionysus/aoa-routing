# Agon Mechanic Guidance

Archive boundary: after `v0.4.0` this subtree is historical. It owns no active
route; send current routing and Agent OS work to `aoa-sdk`. The retained
ownership and placement instructions below describe the pre-archive topology
only and must not be followed as current authority.

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
