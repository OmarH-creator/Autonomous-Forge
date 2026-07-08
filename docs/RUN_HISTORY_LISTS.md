# Run-history lists

`forge run-history-list` lists persisted local run-history JSON records under `.ai/run-history/` without changing files. It is a read-only bridge between reading one explicit record and any future durable history index.

The command performs a non-recursive scan of `.ai/run-history/`, considers only direct `.json` files, sorts records by filename for deterministic output, and summarizes up to `--max-records` entries. It does not write an index, run validation commands, inspect diffs, read changed-file contents, generate patches, approve exceptions, enforce policy decisions, commit, push, call networks, or read environment variables.

## Example

```bash
forge run-history-list --root .
```

For deterministic JSON output:

```bash
forge run-history-list \
  --root . \
  --max-records 20 \
  --format json
```

## Safety checks

The list command keeps the surface narrow:

- It only looks in `.ai/run-history/` below the supplied repository root.
- It scans only direct child files, not nested directories.
- It ignores non-JSON files.
- It reuses the single-record reader schema summary for each JSON record.
- It marks malformed or unsupported JSON records as `refused` instead of failing the whole list.
- It refuses `--max-records` values lower than one.

## Summary fields

The text and JSON summaries include:

- history directory path and status;
- records found, records listed, valid records, and refused records;
- each listed record path;
- readable/refused status;
- selected task identity when available;
- review status;
- preflight overall status;
- commit field;
- refusal reason for malformed or unsupported records.

## Current limitations

This command is intentionally an index preview, not a durable index writer. It does not compare records, verify commits, check workflow status, inspect repository settings, run tests, infer success, mutate `.ai/run-history/`, or persist aggregate state.
