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
- The output path does not already exist; existing records are immutable through this command.

Relative output paths are resolved under `--root`, so `.ai/run-history/latest.json` is valid when `--root .` points at the repository root.

Run-history records are durable project memory, so an existing record is not silently replaced. If another run needs to be persisted, choose a new record path. This command intentionally provides no overwrite escape hatch because run-history is durable project memory.

Confirmed publication is also race-safe. Forge writes the JSON bytes to a same-directory temporary file, flushes and `fsync`s that file, publishes it with an atomic no-clobber hard link, then `fsync`s the containing directory before reporting success. If another process creates the requested output after preflight but before publication, the hard-link step fails and Forge preserves the competing file instead of overwriting it. Temporary files are cleaned on both success and failure.

## Record shape

The persisted JSON payload includes:

- `schema_version`: currently `run-history/v1`.
- `mode`: `opt-in local write`.
- `record`: the same selected-task, review, intent, validation, blocker, and safety-note data used by `forge run-history-preview`.
- `preflight_summary`: the pass/warn/block counts used to gate the write.
- `preflight_next_gate`: the next gate reported by preflight readiness.
- `persistence`: `written by explicit request`.
- `safety_notes`: the write boundary that future maintainers must preserve, including no-clobber publication and file/directory durability syncing.

## Current limitations

This command writes a local history artifact only. It does not append to a long-lived index, rotate files, inspect Git state, compare existing records, detect secrets, run tests, or validate the repository after writing. Callers should still review the output and run the repository test suite separately. Existing records must be preserved or replaced through a separately reviewed/manual recovery process; this command does not merge or reconcile divergent record contents.

No-clobber publication uses a same-filesystem hard link, so the underlying filesystem must support ordinary hard links. The temporary file is deliberately created in the output directory so publication cannot cross filesystem boundaries.
