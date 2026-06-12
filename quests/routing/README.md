# Routing Quest Lane

This lane holds schema-backed `AOA-RT-Q-*.yaml` source quest records for
`aoa-routing`.

Use lifecycle state directories:

```text
quests/routing/<state>/AOA-RT-Q-####.yaml
```

The state directory must match the YAML `state` field. `scripts/validate_router.py`
checks that contract for routing quest records.
