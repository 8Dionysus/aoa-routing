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

The fourteen historical output paths and `aoa_routing_thin_router_v1` stay
available as rollback and compatibility evidence. Their presence does not
make this repository canonical.

Consumer-zero is still false at this stage. The compatibility window remains
active, the rollback implementation remains retained, and archive execution
is forbidden. A later archive-ready receipt must prove those conditions; an
actual hosting archive still requires a separate exact operator approval.
