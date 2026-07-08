# Executor Observation Audits

`forge executor-observation-audit` is a read-only review surface for saved validation observations across direct `.ai/run-history/*.json` records.

It exists to give maintainers one conservative checkpoint after `forge executor-run` and `forge executor-handoff-persist`, but before any future patch generation, diff inspection, implementation execution, commit verification, or workflow-status polling.

## Usage

```bash
forge executor-observation-audit \
  --root . \
  --max-records 20 \
  --format json
```

Use `--require-clear` when the audit should act as a fail-closed gate before patch-adjacent work:

```bash
forge executor-observation-audit \
  --root . \
  --max-records 20 \
  --require-clear \
  --format json
```

The command scans only direct JSON files under `.ai/run-history/`. It does not recurse into subdirectories, does not follow symlinks, and inherits the run-history index safeguards for malformed or refused records. Candidate records are sorted by filename. When `--max-records` limits the view, the newest filename-sorted records are audited, so a small limit does not silently prefer older evidence over the latest saved observations. Without `--require-clear`, the command exits successfully after printing the read-only audit unless the audit itself is malformed or refused. With `--require-clear`, it returns a failing exit code unless the aggregate executor-observation status is `clear`.

## Output

The audit reports:

- history directory status;
- records found and records listed;
- aggregate observation counts;
- an overall conservative status;
- each record's validation execution, validation result, validation guard, commit value, and executor-observation status;
- per-record review notes;
- the underlying run-history index validation guard.

Executor-observation statuses are intentionally conservative:

- `observed-clear` means the saved record has a clear passed validation observation.
- `observed-blocked` means the saved record has a failed validation observation and must block patch-adjacent work.
- `missing-observation` means the saved record has no validation observation.
- `needs-review` means the saved record has skipped, unknown, or internally inconsistent observation fields.
- `refused` means the record could not be safely read by the run-history index.

## Safety boundary

This command does not change files, run validation commands, check workflow status, inspect diffs, generate patches, verify commits, grant approvals, or enforce policy. It only summarizes saved local record fields so a later workflow can decide whether executor evidence is strong enough to proceed. `--require-clear` changes only the process exit code; it still does not mutate files or approve work.
