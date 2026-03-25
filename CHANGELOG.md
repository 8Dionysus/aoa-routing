# Changelog

All notable changes to `aoa-routing` will be documented in this file.

The format is intentionally simple and human-first.
Tracking starts with the community-docs baseline for this repository.

## [Unreleased]

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
