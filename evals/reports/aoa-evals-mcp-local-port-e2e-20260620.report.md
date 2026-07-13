---
schema_version: local_eval_report_note_v1
owner_repo: aoa-routing
status: draft
title: aoa-evals MCP local-port E2E smoke
summary: Records the first live aoa-evals-mcp end-to-end write path through aoa-routing's
  repo-local eval port without central proof promotion.
refs:
- evals/PORT.yaml
- evals/intake/aoa-routing-advisory-route-authority-boundary.eval_need.json
- evals/README.md
- routing/two-stage-skill-selection/README.md
- routing/two-stage-skill-selection/docs/two-stage-skill-selection.md
- repo:aoa-evals/docs/architecture/AOA_EVALS_MCP_CONTRACT.md
- repo:aoa-evals/evals/boundary/aoa-approval-boundary-adherence/EVAL.md
- repo:aoa-evals/evals/boundary/aoa-experience-protocol-integrity/EVAL.md
- repo:aoa-evals/evals/boundary/aoa-stats-regrounding-boundary-integrity/EVAL.md
authority_boundary: no verdict, scoring, regression, or proof doctrine authority
---

## Scope

This local report records a live `aoa-evals-mcp` end-to-end smoke through the `aoa-routing` repo-local eval port.

It is an `aoa-routing` local report note. It is not a central `aoa-evals` verdict, score, regression marker, proof receipt, or bundle promotion.

## Method

1. Used the live `aoa_evals` MCP access plane to list workspace local ports with skeleton ports included.
2. Inspected `aoa-routing` through `aoa_evals_local_port` and confirmed a valid skeleton port.
3. Ran `aoa_evals_find_or_propose_local` for the routing-local authority-boundary pressure around owner-layer shortlist hints and optional two-stage skill selection.
4. Reviewed nearest central eval refs before accepting a local intake path.
5. Ran `aoa_evals_write_local_intake` with `apply=false` and confirmed schema-valid dry-run output.
6. Applied the same packet with `apply=true`, writing one local intake packet and activating `evals/PORT.yaml`.
7. Re-inspected the port through MCP and ran the owning `aoa-evals` local-port
   validator against `aoa-routing`.

## Observed Result

- Initial port status: `skeleton`.
- Final port status: `active`.
- Local intake count: `1`.
- Written intake packet: `evals/intake/aoa-routing-advisory-route-authority-boundary.eval_need.json`.
- Local-port validator result: `ok: true` with no issues.
- Central `aoa-evals` source was not mutated.

## Web-Practice Alignment

Current agent-eval guidance emphasizes evaluating workflow traces, tool calls, handoffs, and routing behavior, not only final answers. This smoke therefore targeted the MCP workflow trajectory:

`inspect local port -> find/propose -> dry-run write -> apply -> re-inspect -> validate`.

The selected local pressure also follows that posture: it concerns whether generated routing hints and two-stage skill routing stay advisory and route to stronger owners instead of becoming activation or proof authority.

## Boundaries

- `aoa-routing` owns this local pressure packet and local report note.
- `aoa-evals` remains the owner of central proof doctrine, verdicts, scoring, regression authority, and any later bundle adoption.
- `aoa-evals-mcp` is an access plane and narrow local write convenience, not proof authority.
- This report does not prove the generated router is globally correct.
- This report does not prove the candidate should become a central eval bundle.

## Next Route

The next useful route is runtime adoption of the `aoa-eval` skill: verify that the live Codex root sees the skill, that trigger phrases route into `aoa-eval`, and that the skill uses local ports and central `aoa-evals` in the right order.
