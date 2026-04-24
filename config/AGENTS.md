# AGENTS.md

## Guidance for `config/`

`config/` holds routing build, policy, and publication inputs.

Config may shape generated route surfaces, but it must not invent source-owned meaning or override owner repos.

Keep config explicit, public-safe, and reproducible. Avoid hidden workspace assumptions, private paths, and local-only magic.

When config changes route output, rebuild and inspect generated route maps for source-ref fidelity, route-boundary drift, and low-context posture.

Verify with:

```bash
python scripts/build_router.py --check
python scripts/validate_router.py
python scripts/validate_semantic_agents.py
```
