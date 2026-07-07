# Run-history writes

`forge run-history-write` is the first intentionally write-capable command in Autonomous Forge. It writes exactly one local JSON file only when the caller explicitly asks for it and the current preflight readiness checklist has no blocking checks.

The command is designed as a narrow persistence step, not as an executor. It does not run validation commands, inspect diffs, read changed-file contents, generate patches, approve exceptions, enforce policy decisions, commit, push, call networks, or read environment variables.

## Example

```bash
forge run-history-write \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --output .ai/run-history/latest.json \
  --confirm-write
```

## Safety gates

The writer refuses to persist a record unless all of these are true:

- `--confirm-write` is present.
- The preflight readiness summary has zero blocking checks.
- The output path stays inside the repository root.
- The output path is under `.ai/run-history/`.
- The output path uses a `.json` extension.

Relative output paths are resolved under `--root`, so `.ai/run-history/latest.json` is valid when `--root .` points at the repository root.

## Record shape

The persisted JSON payload includes:

- `schema_version`: currently `run-history/v1`.
- `mode`: `opt-in local write`.
- `record`: the same selected-task, review, intent, validation, blocker, and safety-note data used by `forge run-history-preview`.
- `preflight_summary`: the pass/warn/block counts used to gate the write.
- `preflight_next_gate`: the next gate reported by preflight readiness.
- `persistence`: `written by explicit request`.
- `safety_notes`: the write boundary that future maintainers must preserve.

## Current limitations

This command writes a local history artifact only. It does not append to a long-lived index, rotate files, inspect Git state, compare existing records, detect secrets, run tests, or validate the repository after writing. Callers should still review the output and run the repository test suite separately.
