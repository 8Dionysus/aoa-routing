# SDK Shadow Release Parity Consumer

This gate is the predecessor-side M1 consumer for the routing producer
succession accepted by `AOA-RT-D-0004`.

Its posture is deliberately narrow:

- `aoa-routing` remains the canonical producer;
- `aoa-sdk v0.6.0` is admitted only as a non-publishing shadow producer;
- the stable ABI remains `aoa_routing_thin_router_v1`;
- no G4 or G5 receipt is implied;
- no runtime consumer, mirror, publication route, or archive authority changes.

## Exact Release Pin

`config/sdk_shadow_release_pin.json` binds the check to:

- annotated tag `v0.6.0`;
- annotated tag object `14e34a7eb5515dbb788c7fa1373dbcaf43d51163`;
- source commit `f3e23b60ec483ce81f5abe9aafe7303c15df2102`;
- package version `0.6.0`;
- predecessor implementation baseline
  `7e2fe467ad26aa645b61849001a456dda4562ffc`;
- the exact compact input archive and its SHA-256;
- all fourteen input-source refs and all fourteen output names;
- the release-artifact workflow observation and wheel/sdist hashes.

The workflow artifact expires. Its IDs and hashes are historical release
evidence, not the durable package fetch path or an authority grant. The
durable executable pin is the exact annotated tag, peeled source commit, and
source-contained fixture/hash contract.

The gate reports the SHA-256 of its locally rebuilt wheel but does not equate
that archive hash with the CI wheel hash: wheel container metadata is not yet
declared reproducible. Instead it proves the exact tagged source, installed
package version and import location, packaged schema set, dual provenance, and
all output bytes. Reproducible wheel-container identity remains a separate
supply-chain hardening question rather than a hidden M1 assertion.

## Gate Sequence

`scripts/verify_sdk_shadow_release_parity.py` fails closed unless it can:

1. validate the pin against its strict schema;
2. prove the SDK checkout is clean, at the exact source commit, has the exact
   package version, and carries an annotated tag that peels to that commit;
3. prove the predecessor compiler, schemas, and entry script have not changed
   since the M1 baseline;
4. hash and safely materialize the exact compact fixture archive, rejecting
   absolute paths, traversal, duplicate paths, links, and non-file members;
5. build a wheel from the exact SDK release checkout;
6. install that wheel and its runtime dependencies in a fresh virtual
   environment with `PYTHONPATH` removed;
7. import the routing implementation from that environment rather than either
   source checkout;
8. build and validate the SDK shadow bundle with exact dual-producer and
   input-source provenance;
9. run the unchanged canonical predecessor on the same fixture;
10. require 14/14 byte equality and equality with the release-contained
    predecessor hash manifest.

The generated comparison products live only in a temporary directory. The
gate never writes `generated/`, publishes an artifact, or mutates a runtime
mirror.

## Stop Line

Any unexplained byte, schema, hash, package, tag, source, input, or provenance
difference stops the release gate. The mismatch must be repaired or admitted
later as a separately designed ABI change. This consumer cannot waive it and
cannot promote the SDK to canonical producer.
