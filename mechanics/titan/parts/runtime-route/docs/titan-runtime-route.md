# Titan Runtime Route

The runtime route maps operator intent to the Titan service cohort.

## Intent routing

| Intent | Active Titans | Notes |
|---|---|---|
| session orientation | Atlas, Sentinel, Mneme | default explicit summon |
| repository mapping | Atlas, Sentinel | read-only |
| risk review | Sentinel | read-only |
| provenance and closeout | Mneme | read-only |
| implementation | Atlas, Sentinel, Mneme, Forge | Forge requires mutation gate |
| verdict or comparison | Atlas, Sentinel, Mneme, Delta | Delta requires judgment gate |
| implementation plus verdict | Atlas, Sentinel, Mneme, Forge, Delta | both gates required |

## Route law

Route selection must be recorded in a session receipt when it changes active Titans.

## Stop rules

- Never route Forge from vague enthusiasm.
- Never route Delta from taste alone.
- Never route Mneme into final memory writeback without owner acceptance.
- Never let route state override source-owned role surfaces.
