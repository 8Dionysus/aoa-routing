# Releasing `aoa-routing`

This guide defines the bounded publication route for the thin routing layer.
Root `AGENTS.md` and the nearest nested route card own executable validation;
this document owns release-readiness shape and closeout expectations.

## Operating Card

| Field | Route |
| --- | --- |
| role | public release-readiness guide for routing projections and contracts |
| input | version target, complete tag-to-main history, generated parity, PR and CI state |
| output | landed main, matching tag, changelog-derived GitHub Release, verified postpublish state |
| owner | root route law for execution; this guide for publication shape |
| next route | `CHANGELOG.md`, `README.md`, `ROADMAP.md`, `scripts/release_check.py`, GitHub PR and Release |
| validation | root release gate, Repo Validation, landed-main rerun, release audit |

## Maintenance Publication Shape

Ordinary paired routing releases ended at G5. A rare predecessor maintenance
publication is ready only when a compatibility, security, rollback, or
deprecation need is named explicitly and:

- `CHANGELOG.md` has a dated section with Summary, Validation, and Notes;
- the M3 maintenance-only validator accepts the exact SDK owner receipt,
  retained rollback implementation, compatibility ABI, and archive posture;
- the gate derives the immutable M3 base in CI and local release runs;
- the diff contains no new or structural implementation path, generated
  output, feature lane, or publication contour;
- any modified retained source blob is covered by an owner-reviewed approval
  packet for exactly one compatibility, security, rollback, or deprecation
  class, exact path, exact resulting Git blob, and durable approval reference;
- the repository-local maintenance gate passes without sibling checkout;
- the release branch lands through PR and GitHub Repo Validation;
- landed `main` passes the same gate before any tag is created;
- the GitHub Release body is derived from the canonical changelog section;
- postpublish audit confirms branch, tag, latest release, body sync, and clean
  canonical worktree.

## Routing Boundaries

Release notes may describe routing projections, contracts, and owner-return
paths. They must not present routed source meaning, eval verdicts, KAG content,
memory truth, shared statistics, or runtime state as routing-owned authority.

Artifact identity and a trust-gate verdict prove the bounded routing readmodel
handoff named by the manifest. They do not certify the upstream objects to
which the router points.

The M1 shadow release and M2 conditional handoff are immutable historical
evidence. They do not authorize a new paired release or reopen predecessor
producer ownership. The M3 packet is the active release boundary.

## Version Surfaces

When a release marker moves, inspect together:

- `README.md`;
- `CHANGELOG.md`;
- `ROADMAP.md`;
- `tests/test_roadmap_parity.py`;
- any generated surface whose builder consumes the changed source text.

## Public-Share Review

Keep release notes free of secrets, private topology, raw operational traces,
and live host values. Summarize validation, name exact public owner boundaries,
and preserve enough history for a later contributor to reproduce the scope.

## Closeout

After publication, verify the remote tag and GitHub Release, confirm local
`main` equals `origin/main`, and report any skipped check or unresolved owner
dependency. A local tag or green feature branch is not a completed release.
