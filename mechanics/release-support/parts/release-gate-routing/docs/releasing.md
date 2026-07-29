# Releasing `aoa-routing`

`aoa-routing` was released as the predecessor thin navigation and dispatch
layer of AoA. `v0.4.0` is its final release.

See also:

- [README](../../../../../README.md)
- [CHANGELOG](../../../../../CHANGELOG.md)

## Historical pre-archive maintenance publication flow

Before `v0.4.0`, the following flow governed an explicitly named
compatibility, security, rollback, or deprecation need:

1. Keep the change inside the maintenance-only boundary.
2. When an already retained source file must change, obtain owner review and
   add one `aoa_routing_maintenance_approval_v1` packet that binds the allowed
   class, immutable M3 base, exact path, resulting Git blob, and durable
   approval reference. The packet cannot approve itself or admit a new path.
3. Update `CHANGELOG.md` in the `Summary / Validation / Notes` shape.
4. Run the repo-level verifier:
   - `python scripts/release_check.py`
   - the verifier must accept the exact M3 maintenance-only packet;
   - it must derive the immutable M3 base and reject unapproved retained-source
     changes, new or structural implementation paths, generated outputs,
     publication, or sibling checkouts;
   - M1 and M2 remain historical evidence, not active release dependencies.
5. If you need the wider workspace-level federation preflight in addition to the
   repo-local verifier and current CI route, run:
   - `aoa release audit /srv --phase preflight --repo aoa-routing --strict --json`
6. Publish only through `aoa release publish`.

This flow is preserved for audit and reproduction only. After `v0.4.0`, do not
publish or maintain this predecessor. Route every routing release request to
`aoa-sdk`; any future predecessor publication would require an explicit
unarchive decision and new exact operator authorization.
