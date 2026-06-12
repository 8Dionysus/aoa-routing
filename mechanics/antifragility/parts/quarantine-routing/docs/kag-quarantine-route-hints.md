# KAG Quarantine Route Hints

## Core rule

KAG quarantine signals narrow routing posture; they do not replace KAG truth.

Quarantine hints stay additive and never replace KAG authored truth.

## Inputs

The composite stress-route overlay may read only:

- `aoa-kag/examples/projection_health_receipt.example.json`
- `aoa-kag/examples/regrounding_ticket.example.json`
- `aoa-stats/generated/stress_recovery_window_summary.min.json`

These surfaces already name the degraded or quarantined state in a structured
form. Routing consumes that structure and stays thin.

## Allowed Routing Effects

- prefer `source_first_until_pass` posture when KAG says the projection is degraded
- point at the bounded regrounding ticket instead of inventing a repair plan
- keep degraded continuation visible when the playbook gate allows it

## Forbidden Routing Effects

- silent re-open of blocked actions
- synthetic KAG health scores invented by routing
- replacement of source-owned `projection_health_receipt` meaning
- parsing authored KAG docs as a hidden authority layer

## Memo Interaction

Memo recovery patterns may appear as reviewed context beside KAG quarantine
signals. They remain recall aids, not proof and not health authority.
