# Cross-Repo Router Bridge

Skill capability routing is a cross-repo bridge between `aoa-skills` and
`aoa-routing`.

The ownership split is deliberate.

## `aoa-skills` owns

- the compact catalog of independently callable bundles
- capability identity, primary parent, typed relations, ABI, and lifecycle
- binding, trust, applicability, compatibility, and retrieval documents
- invocation and visibility posture

These are derived from source-owned skill meaning and must stay aligned with the live skill canon.

## `aoa-routing` owns

- the thin skill registry projection
- bounded inspect and expand navigation
- owner-qualified lifecycle and trust hints needed for routing
- strict failure when catalog, graph, or typed eval dependencies disagree

These are routing decisions, not skill meaning.

## What the bridge must not do

- `aoa-skills` must not become a cross-repo dispatch authority
- `aoa-routing` must not become a second skill canon
- routing must not activate a skill or persist a task-local execution DAG
- router outputs must not copy full capability contracts or retrieval documents

The practical contract is:

- `aoa-skills` publishes the agent catalog and capability graph
- `aoa-routing` projects callable bundles and points deep retrieval back to the graph
- the session or runtime composes any task-local DAG, while stable sequences
  route to their workflow or playbook owner
