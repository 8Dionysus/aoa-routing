# RPG Parts

## navigation-bridge

| Field | Route |
| --- | --- |
| role | publish an example-only RPG navigation bundle |
| input | source quest dispatch, playbook party-template cards, eval unlock-proof cards |
| output | derived navigation cards for inspect/expand/handoff |
| owner | `mechanics/rpg/parts/navigation-bridge/` |
| next route | source quest, playbook template, eval proof, or owner handoff |
| verification | `validate_rpg_navigation_bridge_surface` |

The part does not add accept, claim, complete, reward, or unlock verbs.
