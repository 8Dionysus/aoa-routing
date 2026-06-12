# VIA_NEGATIVA_CHECKLIST

This checklist is for `aoa-routing` as the thin navigation and dispatch hints.

## Keep intact

- route hints that answer where to go next
- evidence-aware suppression semantics
- owner receipts and bounded proof as the main grounding signals

## Merge, move, suppress, quarantine, deprecate, or remove when found

- hints that explain what happened instead of where to go
- routing logic sourced from memo-only recall or vague confidence
- overlapping hint families that can collapse into one clearer hint

## Questions before adding anything new

1. Is this navigation, or is it secretly meaning or policy?
2. Would a narrower hint plus suppression be safer than a broad rule?
3. Does this hint have stronger owner grounding than anecdote?

## Safe exceptions

- short-lived migration hints with explicit expiry
- generated hint variants only when consumers truly need separate shapes

## Exit condition

- Routing should stay legible as direction, not narration.
