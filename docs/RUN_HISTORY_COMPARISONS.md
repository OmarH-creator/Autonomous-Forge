# Run-history comparisons

`forge run-history-compare` compares two explicit persisted local run-history JSON records without changing files.

It is a read-only bridge between listing/selecting saved records and any future validation-status reader, durable index writer, validation executor, diff inspection, or patch workflow.

## Usage

```bash
forge run-history-compare \
  --root . \
  --before .ai/run-history/older.json \
  --after .ai/run-history/latest.json
```

For deterministic JSON output:

```bash
forge run-history-compare \
  --root . \
  --before .ai/run-history/older.json \
  --after .ai/run-history/latest.json \
  --format json
```

## Compared fields

The comparison reuses the supported single-record reader summary for both records, then reports each field as `changed` or `unchanged`:

- task identity and metadata;
- review status;
- preflight overall status;
- validation execution mode;
- validation result;
- changed-files summary;
- commit field;
- blockers;
- safety notes.

## Safety checks

The command keeps the surface narrow:

- Both record paths must be under `.ai/run-history/` below the supplied repository root.
- Both paths must use a `.json` extension.
- Both records must use the supported `run-history/v1` schema.
- Malformed or unsupported records are refused with a clear error.
- The command compares only explicit records; it does not scan the history directory or select records automatically.

## Current limitations

This command does not verify commits, check workflow status, inspect repository settings, run tests, inspect diffs, read changed-file contents, generate patches, infer success, write indexes, mutate `.ai/run-history/`, enforce policy decisions, call networks, commit, or push.
