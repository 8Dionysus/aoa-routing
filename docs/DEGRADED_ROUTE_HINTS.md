# DEGRADED ROUTE HINTS

## What this family is for

A degraded route hint tells an agent what to read or do next when a source-owned surface is already known to be under stress.

The hint should answer:

- what surface is affected
- what stress pattern matters
- what navigation posture should be used
- what bounded next hops are preferred
- whether evidence is strong enough to activate the hint

## Suggested builder posture

The builder should stay thin.

Prefer one of these inputs:

1. sibling generated export surfaces from owner repos
2. an explicit reviewed manifest of owner-local receipt refs
3. fixture-backed tests that model the intended hint family

Avoid open-ended live crawling of arbitrary logs.

## Hint anatomy

A useful hint includes:

- a selector for repo, surface, and optional stressor family
- a preferred navigation posture
- a bounded next-hop list
- evidence references
- optional contextual references
- a suppression state
- optional expiry

## Example reading order under stress

For a degraded hybrid-query family:

1. inspect the owner-local degraded artifact
2. inspect the owner-local doctrine for that degraded family
3. reground via a bounded technique or source authority
4. only then consider broader routing or mutation lanes

## Expiry and drift

Stress hints should not become immortal folklore.

Use one or more of:

- explicit expiry timestamps
- build-time pruning of stale hint inputs
- suppression when the evidence window becomes too thin
- replacement through superseding hints

## Relationship to other routing families

Stress hints should complement, not replace:

- task-to-surface hints
- recommended paths
- return-navigation hints
- federation entrypoints

They are a stress overlay, not a new sovereign router.
