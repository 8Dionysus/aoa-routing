# Releasing `aoa-routing`

`aoa-routing` is released as the thin navigation and dispatch layer of AoA.

See also:

- [README](../README.md)
- [CHANGELOG](../CHANGELOG.md)

## Recommended release flow

1. Keep the release bounded to routing and dispatch surfaces.
2. Update `CHANGELOG.md` in the `Summary / Validation / Notes` shape.
3. Run the repo-level verifier:
   - `python scripts/release_check.py`
4. Run federation preflight:
   - `aoa release audit /srv --phase preflight --repo aoa-routing --strict --json`
5. Publish only through `aoa release publish`.
