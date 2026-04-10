# Changelog

All notable changes to `aoa-routing` will be documented in this file.

The format is intentionally simple and human-first.
Tracking starts with the community-docs baseline for this repository.

## [Unreleased]

## [0.2.0] - 2026-04-10

### Added

- additive federation-mesh expansion for runtime, profile, and owner-owned
  entry capsules plus checkpoint-starter handoffs
- technique-kind second-cut routing, composite stress-route hints, and
  stronger tiny-model starter smoke coverage

### Changed

- retargeted federation routing through owner capsules, language-neutral v2
  envelopes, and tighter thin-router validation contracts
- aligned wave-9 two-stage artifacts, generated eval cases, and current
  `aoa-skills`-driven precision behavior on `main`
- aligned two-stage precision expectations with the current stage-2 router
  policy so contract-boundary prompts now activate `aoa-contract-test` while
  thinner generic bounded-change prompts stay below the activation threshold
- regenerated routing and two-stage eval artifacts after the precision-case
  refresh

### Included in this release

- routing-surface expansion across `docs/`, `generated/`, `config/`, `schemas/`,
  `examples/`, `scripts/`, and `tests/`, including federation-mesh owner
  capsules, checkpoint starter handoffs, owner-layer shortlist routing, ToS
  return-navigation tightening, and memo return-capsule cross-validation
- repo-local operating and follow-through surfaces under `.agents/`, `.github/`,
  `QUESTBOOK.md`, `quests/`, `AGENTS.md`, `README.md`, and `CONTRIBUTING.md`,
  including project-foundation rollout, validation-pin refreshes, and
  thin-router and tiny-starter contract hardening

## [0.1.0] - 2026-04-01

First public baseline release of `aoa-routing` as the thin navigation and federation-entry layer in the AoA public surface.

This changelog entry uses the release-prep merge date.

### Summary

- first public baseline release of `aoa-routing` as the navigation and dispatch layer for AoA
- the public baseline now ships core routing outputs, pairing and return-navigation hints, federation-entry surfaces, and the optional two-stage low-context routing seam
- this release keeps source ownership explicit by routing to source-owned capsules, sections, and entry surfaces instead of recreating their meaning

### Added

- community-docs baseline established for this repository
- `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `CONTRIBUTING.md`
- `docs/FEDERATION_ENTRY_ABI.md` as the doctrine surface for the federation entry orientation layer
- `generated/federation_entrypoints.min.json` and its schema-backed validation path
- additive `federation_queries` and `federation_starters` in `generated/tiny_model_entrypoints.json`
- build, validation, and CI support for `Agents-of-Abyss`, `Tree-of-Sophia`, `aoa-playbooks`, and `aoa-kag` as federation entry inputs
- narrow support for `Tree-of-Sophia/examples/tos_tiny_entry_route.example.json` as a source-owned ToS tiny-entry handoff surface

### Changed

- `tos-root` in `generated/federation_entrypoints.min.json` now hands off first to the source-owned ToS tiny-entry route while keeping `README.md` and `CHARTER.md` as root card surfaces
- `docs/FEDERATION_ENTRY_ABI.md`, `README.md`, and `ROADMAP.md` now describe the ToS tiny-entry sync as additive and non-authoritative
- `generated/federation_entrypoints.min.json` now publishes a second live `kag_view` for `Tree-of-Sophia`, while `kag-view-root` stays defaulted to `aoa-techniques`
- ToS tiny-entry input validation now accepts `bounded_hop` as the primary hop field and keeps `lineage_or_context_hop` as a compatibility alias during the current transition window
- memo recall hints now publish mode-indexed `capsule_surfaces_by_mode` for router-ready doctrine and parallel object-facing recall when upstream `aoa-memo` contracts expose a capsule step

### Included in this release

- core routing outputs under `generated/`, including `aoa_router.min.json`, `task_to_surface_hints.json`, `recommended_paths.min.json`, and `task_to_tier_hints.json`
- federation-entry and return-navigation surfaces under `generated/federation_entrypoints.min.json`, `generated/return_navigation_hints.min.json`, and `docs/FEDERATION_ENTRY_ABI.md`
- the optional low-context routing family under `generated/tiny_model_entrypoints.json` and the `two_stage_*` generated surfaces

### Validation

- `python scripts/build_router.py --check`
- `python scripts/validate_router.py`
- `python scripts/build_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills --check`
- `python scripts/validate_two_stage_skill_router.py --routing-root . --skills-root ../aoa-skills`
- `pytest -q`

### Notes

- this release establishes routing as a navigation layer only; it does not make `aoa-routing` the authority surface for the repositories it reads
