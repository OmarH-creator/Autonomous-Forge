# Preflight Readiness

`forge preflight-readiness` prints a conservative checklist for whether the current read-only planning surfaces are ready for a future opt-in persistence design.

It is a review surface only. It combines the run-history preview record shape with repository inventory file-presence signals, then reports pass, warn, and block statuses for the selected task, review artifact, patch intent, validation preview, execution boundary, persistence boundary, durable blockers, and required repository files.

## Example

```bash
forge preflight-readiness \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

For deterministic machine-readable output:

```bash
forge preflight-readiness \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

## Stable fields

The JSON output includes:

- `title`: `Autonomous Forge preflight readiness checklist`.
- `mode`: always `read-only`.
- `source`: `run-history preview plus repository inventory`.
- `selected_task`: selected task ID, title, priority, and status before any run.
- `checks`: ordered readiness checks with `name`, `status`, and `reason`; inventory also includes checked and missing paths.
- `summary.overall_status`: `ready for opt-in persistence design`, `needs review`, or `blocked`.
- `summary.pass`, `summary.warn`, and `summary.block`: deterministic counts by check status.
- `next_gate`: the next safe product gate.
- `safety_boundary`: explicit non-execution and non-persistence boundary.

## Safety boundary

`forge preflight-readiness` does not write history files, change repository files, inspect diffs, read changed-file contents, generate patches, run validation commands, read environment variables, or call networks.

Future persistence work should remain separate and explicitly opt-in. This checklist only reports whether the existing review, patch-intent, validation-preview, run-history-preview, and inventory signals look ready for that design step.
