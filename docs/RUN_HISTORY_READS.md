# Run-history reads

`forge run-history-read` reads and summarizes one persisted local run-history JSON record. It is a read-only companion to `forge run-history-write` and exists so maintainers can inspect a saved record before any history index, validation executor, or patch workflow is added.

The command reads exactly one JSON file supplied by `--record`. It does not scan the history directory recursively, follow symlinked records, run validation commands, inspect diffs, read changed-file contents, generate patches, approve exceptions, enforce policy decisions, commit, push, call networks, or read environment variables.

## Example

```bash
forge run-history-read \
  --root . \
  --record .ai/run-history/latest.json
```

For deterministic JSON output:

```bash
forge run-history-read \
  --root . \
  --record .ai/run-history/latest.json \
  --format json
```

## Safety checks

The reader refuses to summarize a record unless all of these are true:

- The record path stays inside the repository root.
- The record path is under `.ai/run-history/`.
- The record path uses a `.json` extension.
- The record is a real file, not a symlink.
- The record is a file, not a directory.
- The JSON payload uses the supported `run-history/v1` schema.
- The core `record`, `record.task`, and `preflight_summary` fields are JSON objects.

## Summary fields

The text and JSON summaries include:

- source path;
- top-level and nested record schema versions;
- selected task identity and status before the run;
- review status and attention flag;
- validation execution/result fields;
- changed-files summary and commit field;
- preflight pass/warn/block summary;
- persistence mode;
- blockers;
- safety notes.

## Current limitations

This command intentionally reads one explicit real JSON record only. It does not list records, follow symlinked records, build a durable index, compare runs, verify commits, check workflow status, inspect repository settings, run tests, or infer success beyond the contents of the selected JSON record.
