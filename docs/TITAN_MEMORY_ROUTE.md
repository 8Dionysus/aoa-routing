# Titan Memory Route

Memory routes are read-mostly. They lead from recall result to source owner.

```text
recall query -> Memory Loom record -> source_ref/session_id -> owner repo/source seed -> operator decision
```

Forge is not part of memory route unless a mutation is explicitly approved. Delta is not part of memory route unless a judgment is explicitly requested.
