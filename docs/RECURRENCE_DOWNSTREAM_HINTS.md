# Recurrence downstream hints for routing

`aoa-routing` may consume recurrence projections only as thin navigation hints.

Allowed generated candidates:

- `generated/recurrence_owner_hints.min.json`
- `generated/recurrence_return_hints.min.json`
- `generated/recurrence_gap_hints.min.json`

Each hint must remain advisory and point back to owner/source surfaces. A recurrence hint must not become semantic truth, proof authority, skill activation authority, KAG policy, or full graph traversal.
