# AGENTS.md

Local route card for `aoa-routing/evals/`.

This skeleton port captures future routing eval pressure without making
`aoa-routing` a proof owner.

`aoa-evals` owns central verdict, scoring, regression, and proof doctrine
authority. Keep route policy and route hints in `aoa-routing`; route central
proof adoption to `aoa-evals`.

Validation:

```bash
python ../aoa-evals/scripts/validate_local_eval_port.py --target-root .
```
