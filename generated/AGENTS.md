# AGENTS.md

This file applies to tracked routing artifacts under `generated/`.

## Role of this directory

Everything in `generated/` is a derived routing surface.
These files help models choose the next bounded source-owned surface to inspect.
They are not a second canon and they do not own upstream meaning.

The current generated set includes:

- `cross_repo_registry.min.json` as the normalized registry of routeable objects
- `aoa_router.min.json` as the thin projection surface and ABI-bearing root of
  the OS Abyss routing readmodel bundle
- `task_to_surface_hints.json` as inspect, expand, pair, and recall dispatch hints
- `task_to_tier_hints.json` as task-family dispatch hints derived from `aoa-agents`
- `quest_dispatch_hints.min.json` as the first live source-only quest inspect, expand, and handoff routing surface
- `recommended_paths.min.json` as bounded upstream and downstream hops
- `owner_layer_shortlist.min.json` as boundary-owned owner-layer advisory hints
- `kag_source_lift_relation_hints.min.json` as bounded direct relation hints for the KAG/source-lift seam
- `pairing_hints.min.json` as bounded pair suggestions
- `federation_entrypoints.min.json` as the federation-entry orientation surface
- `stats_regrounding_hints.min.json` as boundary-owned stats re-grounding advisory hints
- `tiny_model_entrypoints.json` as the compact starter and query seam for low-context routing

## Editing posture

Do not hand-edit derived payloads here as the normal workflow.
Change the builder or the source-owned inputs, then regenerate the outputs.

Keep every generated file:

- compact, deterministic, and schema-backed
- explicit about repo refs and next hops
- free of copied capsule text, section text, or other source-owned payload bodies
- bounded enough that routing still acts like navigation rather than meaning-authoring
- aligned with `docs/artifact-bundles/thin_router.bundle.json` when
  `aoa_router.min.json` artifact identity, subject set, or consumer expectation
  changes

If a task really requires an intentional generated change, report which file changed and whether its output shape changed.

## Validation

After changing generation logic or any upstream routing contract, run:

```bash
python scripts/build_router.py
python scripts/validate_router.py
python scripts/build_router.py --check
python scripts/validate_abyss_machine_routing_bundle.py
python mechanics/agon/parts/gate-routing/scripts/build_agon_gate_routing_registry.py --check
python mechanics/agon/parts/gate-routing/scripts/validate_agon_gate_routing.py
python -m pytest -q tests
```

The validator should confirm rebuild parity, schema integrity, live quest hint integrity, and source-owned inspect and expand targets.
