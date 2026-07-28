# Routing Succession M3 Maintenance-Only Posture

`aoa-sdk v0.8.0` is the canonical routing producer. This predecessor is now a
compatibility, security, rollback, and deprecation surface only.

The active predecessor CI contour no longer:

- checks out the fourteen routing producer inputs;
- rebuilds or validates a competing canonical bundle;
- consumes an SDK shadow release;
- runs a latest-sibling compatibility canary;
- participates in a paired release stream.

`Repo Validation` remains because protected-branch changes still need one
fail-closed maintenance gate. It validates this receipt, repository topology,
decision records, and local tests without publishing or generating routing
artifacts.

The root-owned repository release gate compares every run against the
immutable `maintenance_base_ref` in this packet. Both `.yml` and `.yaml`
workflow contours are inventoried. New, copied, renamed, deleted, or
type-changed non-document predecessor surfaces fail closed, as do all
generated-output changes and publication markers.

An actual compatibility, security, rollback, or deprecation repair may modify
an already retained source file. Such a modification is accepted only when a
reviewed `aoa_routing_maintenance_approval_v1` packet under
`evidence/maintenance-approvals/` matches:

- the immutable M3 maintenance base;
- one allowed maintenance class;
- the exact retained path;
- the exact resulting Git blob;
- a named approval authority and durable approval reference.

The packet is review evidence, not self-approval. Repository owner review
admits it; the validator only proves that the landed blob did not escape the
reviewed scope. It cannot permit new or structural paths, generated outputs, a
competing producer, or publication.

The fourteen historical output paths and `aoa_routing_thin_router_v1` stay
available as rollback and compatibility evidence. Their presence does not
make this repository canonical.

Consumer-zero is still false at this stage. The compatibility window remains
active, the rollback implementation remains retained, and archive execution
is forbidden. A later archive-ready receipt must prove those conditions; an
actual hosting archive still requires a separate exact operator approval.
