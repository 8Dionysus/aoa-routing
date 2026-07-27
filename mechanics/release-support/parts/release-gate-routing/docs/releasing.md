# Releasing `aoa-routing`

`aoa-routing` is released as the thin navigation and dispatch layer of AoA.

See also:

- [README](../../../../../README.md)
- [CHANGELOG](../../../../../CHANGELOG.md)

## Recommended maintenance publication flow

Ordinary paired routing releases ended at G5. Publish this repository only for
an explicitly named compatibility, security, rollback, or deprecation need.

1. Keep the change inside the maintenance-only boundary.
2. Update `CHANGELOG.md` in the `Summary / Validation / Notes` shape.
3. Run the repo-level verifier:
   - `python scripts/release_check.py`
   - the verifier must accept the exact M3 maintenance-only packet;
   - it must reject producer, generated-output, publication, or sibling
     checkout changes;
   - M1 and M2 remain historical evidence, not active release dependencies.
4. If you need the wider workspace-level federation preflight in addition to the
   repo-local verifier and current CI route, run:
   - `aoa release audit /srv --phase preflight --repo aoa-routing --strict --json`
5. Publish only through `aoa release publish`.
