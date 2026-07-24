# Routing Succession M2 Conditional Handoff

This is the predecessor-owned bridge between the landed SDK G4 shadow proof
and a future, separately validated G5 owner switch.

It deliberately does not switch ownership. The current state remains
`predecessor_canonical`, `aoa-routing` remains the only canonical publisher,
the compatibility window has not started, and normal owner-scoped routing
feature work remains valid here. Treating this receipt as maintenance-only,
runtime publication, G5, consumer-zero, archive readiness, or archive
authority is a contract violation.

## Exact admitted evidence

The handoff admits:

- SDK G4 squash merge
  `5cab5840c03b66c22bb07a6d0863bef9e95c7b23`;
- SDK PR `#221`, PR validation run `30102380158`, and post-main run
  `30102545148`;
- exact G4 evidence SHA-256
  `d7cebc8fb19389e18fba83636e816502d2c4134e01ae36811054afaff118ffc8`;
- the immutable `aoa-sdk v0.6.0` shadow release at
  `f3e23b60ec483ce81f5abe9aafe7303c15df2102`;
- the unchanged predecessor rollback implementation from
  `7e2fe467ad26aa645b61849001a456dda4562ffc`;
- the landed M1 predecessor consumer at
  `5c7c0e5784b1642fb2e9e5231609100dacdbf1e3`.

The G4 evidence proves the released shadow producer, compact and full-corpus
parity, package trust, isolated runtime-mirror content assembly, predecessor
consumption, and rollback. It also records that live runtime SDK provenance,
live currency, G5, publication, and archive authority remain false.

## Transition law

Only a separate SDK-owned receipt at the contract path named by the JSON
evidence may trigger the state change. That G5 receipt must prove together:

- `aoa-sdk` is the sole canonical producer while the fourteen public artifact
  names and `aoa_routing_thin_router_v1` remain compatible;
- the live runtime loads an SDK-produced artifact and exposes exact SDK source,
  artifact digest, and an admitted trust verdict;
- registered consumers remain green without making `aoa-routing` a required
  SDK build dependency;
- the predecessor rebuild still reproduces the bundle at the switch;
- the compatibility-window start date and SDK version are recorded.

Runner or wider Agent OS capabilities may not be hidden inside that owner
switch. They remain later, separately reviewable landings.

## Verification

`scripts/verify_routing_succession_m2_handoff.py` validates the strict local
schema, exact SDK G4 checkout and evidence hash, G4 authority ceiling, unchanged
predecessor producer paths, M1 pin identity, paired decision stop-lines, and
the still-false G5, maintenance, live-provenance, compatibility, consumer-zero,
rollback-retirement, and archive gates.
