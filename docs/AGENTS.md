# AGENTS.md

## Guidance for `docs/`

`docs/` explains routing ABI, federation entry, recurrence navigation, stress posture, route reviews, and owner-dispatch seams.

Docs may define navigation semantics, but they must not replace owner repos for skill, technique, eval, memo, agent, playbook, KAG, or runtime meaning.

Keep route posture bounded: pick, inspect, expand, object use, optional pair, optional recall. Do not turn hints into authority.

When docs change a route boundary, re-check schemas, examples, generated surfaces, and the owner repository named by the route.

Verify with:

```bash
python scripts/validate_router.py
python scripts/validate_semantic_agents.py
```
