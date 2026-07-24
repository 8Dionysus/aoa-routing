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

## Release Shape

A release is ready only after:

- `CHANGELOG.md` has a dated section with Summary, Validation, and Notes;
- the release note is reconstructed from the full previous-tag-to-HEAD history,
  source/mechanics owners, decision records, generated outputs, and sibling
  contracts rather than trusting `[Unreleased]` alone;
- public version markers agree across `README.md`, `CHANGELOG.md`, `ROADMAP.md`,
  and their tests;
- generated routing and KAG surfaces are builder-current;
- the repository release gate passes against the exact pinned sibling roots;
- the M1 predecessor consumer builds and clean-installs the exact tagged
  `aoa-sdk v0.6.0` source, then proves 14/14 byte parity without publishing or
  changing canonical ownership;
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

The SDK shadow release consumer is similarly bounded. Its exact tag, source,
wheel-install, fixture, provenance, and byte-parity proof admits only an M1
shadow comparison. It does not pass G4, issue G5, switch runtime consumers,
publish SDK-built routing artifacts, or authorize archive action. Any
unexplained mismatch is a release blocker.

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
