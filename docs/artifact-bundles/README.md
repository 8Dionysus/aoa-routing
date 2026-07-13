# Routing Artifact Bundles

This directory holds OS Abyss artifact-bundle manifests for public routing
readmodels.

## Current bundle

- `thin_router.bundle.json` covers `generated/aoa_router.min.json` as the ABI
  root and includes the generated routing family, schemas, builder, validator,
  and route docs as artifact subjects.

The bundle signs navigation surfaces only. It does not make routing the owner
of technique, skill, eval, memo, playbook, KAG, role, stats, runtime, or Tree
of Sophia meaning.

## Consumer path

The validator rehearses the OS consumer path: build/sign/verify/release-check,
promote durable release-ready evidence with source and host-managed trust-root
metadata, materialize the routing subjects into an isolated subject store, run
an agent-intent trust gate for `aoa-routing`, and read the source-filtered
registry latest record.

Negative checks cover missing ABI, missing SBOM-lite, missing SLSA/in-toto,
wrong external subject digest, private readmodel markers, unverified latest
records, terminal revocation, and missing materialized subject-store state.

## Required controls

- ABI signature: required for the thin router artifact identity.
- SBOM-lite: required as a subject inventory for the generated routing family.
- SLSA/in-toto: required for generated-surface provenance.
- Sigstore/Cosign: deferred until signed release assets exist.
- C2PA: not applicable to routing JSON unless a public media/export pipeline
  appears.

The executable artifact-bundle check is owned by root `AGENTS.md` and
`scripts/validate_abyss_machine_routing_bundle.py`.
