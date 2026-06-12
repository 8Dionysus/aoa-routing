# Titan

`mechanics/titan/` holds routing-local Titan route contracts. It maps Titan
runtime, console, memory, appserver bridge, and runtime case pressure to the
owner surfaces that can act.

## Operating Card

| Field | Route |
| --- | --- |
| role | route Titan-related intent without becoming the Titan runtime or owner memory |
| input | Titan runtime intent, console intent, memory recall location, appserver bridge route, runtime case |
| output | Titan route packet or next owner surface |
| owner | `aoa-routing` owns route shape only; Titan identity, runtime, SDK bridge, memory, proof, and stats stay with stronger owners |
| next route | `parts/runtime-route/`, `parts/console-route/`, `parts/memory-route/`, `parts/appserver-bridge/`, `parts/runtime-case-routing/` |
| validation | Titan route schema tests, runtime case contracts, mechanics topology validation |

## Boundary

Titan route parts do not summon, mutate, remember, or judge. They name the next
route and gate needed before stronger owners act.
