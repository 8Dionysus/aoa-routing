# AGENTS.md

Archive boundary: after `v0.4.0` this subtree is historical. It owns no active
route; send current routing and Agent OS work to `aoa-sdk`. The retained
ownership and placement instructions below describe the pre-archive topology
only and must not be followed as current authority.

`mechanics/questbook/` owns aoa-routing participation in the shared Questbook
mechanic.

Use this mechanic for routing-owned quest discovery seams, quest board
reflections, harvest fanout routing, and the repo-local routing quest source
contract.

Root `QUESTBOOK.md` owns human open-obligation visibility. Root `quests/` owns
source quest record placement. This mechanic owns the operation law, schemas,
examples, validators, and routing seams that keep those records bounded.

Do not parse sibling live `quests/*.yaml` here. Routing consumes generated
quest projections from source repos.

`legacy/` records former flat paths only. Active source quest records do not
live in `legacy/` or part-local `quests/`.
