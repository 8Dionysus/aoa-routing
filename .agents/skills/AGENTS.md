# AGENTS.md

## Guidance for `.agents/skills/`

`.agents/skills/` is an agent-facing companion surface for routing-layer maintenance.

It may help agents inspect route maps, dispatch hints, and federation entrypoints, but it must not author source meaning. Source repos own meaning. Routing repo owns navigation.

Do not hand-edit exported companion files before changing the source route manifest, schema, builder, or docs that own the route surface.

Keep route language low-context, bounded, and source-ref oriented. Do not copy full source-owned capsule payloads into prompt prose or tool descriptions.

Keep everything public-safe: no private paths, secrets, hidden workspace assumptions, or unreduced operator traces.

Verify with:

```bash
python scripts/validate_router.py
python scripts/validate_semantic_agents.py
```
