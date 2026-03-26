# Spark lane for aoa-routing

This file only governs work started from `Spark/`.

The root `AGENTS.md` remains authoritative for repository identity, ownership boundaries, reading order, and validation commands. This local file only narrows how GPT-5.3-Codex-Spark should behave when used as the fast-loop lane.

If `SWARM.md` exists in this directory, treat it as queue / swarm context. This `AGENTS.md` is the operating policy for Spark work.

## Default Spark posture

- Use Spark for short-loop work where a small diff is enough.
- Start with a map: task, files, risks, and validation path.
- Prefer one bounded patch per loop.
- Read the nearest source docs before editing.
- Use the narrowest relevant validation already documented by the repo.
- Report exactly what was and was not checked.
- Escalate instead of widening into a broad architectural rewrite.

## Spark is strongest here for

- routing-surface wording cleanup
- entry-card and dispatch-hint refinement
- generated router output alignment
- schema, test, and validator-adjacent cleanup with local scope
- tight audits that keep routing thin and deterministic

## Do not widen Spark here into

- authoring new source meaning here
- turning routing into memory, KAG, or second-canon behavior
- broad output-shape redesign without explicit need
- heavy graph-like semantic expansion

## Local done signal

A Spark task is done here when:

- the smallest next object is clearer
- routing remains thin and source-owned meaning stays external
- generated outputs are aligned when touched
- determinism and inspectability are preserved
- the documented build / validation flow ran when relevant

## Local note

Spark should act like a sign-maker here, not like a substitute author.

## Reporting contract

Always report:

- the restated task and touched scope
- which files or surfaces changed
- whether the change was semantic, structural, or clarity-only
- what validation actually ran
- what still needs a slower model or human review
