# AGENTS.md

## Guidance for `examples/`

`examples/` demonstrates route decisions, dispatch seams, stress hints, and federation entry objects.

Examples are illustrative and schema-backed. They should show how a route points back to source authority without becoming that authority.

Keep examples low-context and public-safe: no secrets, private paths, hidden workspace details, or copied source-owned capsule payloads.

If an example changes a route decision shape, update the matching schema, docs, generated builder, and tests together.

Verify with:

```bash
python scripts/validate_router.py
python scripts/validate_semantic_agents.py
```
