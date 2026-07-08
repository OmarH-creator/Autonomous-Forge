# Run-history lists and latest selection

`forge run-history-list` lists persisted local run-history JSON records under `.ai/run-history/` without changing files. `forge run-history-latest` selects the latest readable direct JSON record by deterministic filename ordering, also without changing files.

These commands are read-only bridges between reading one explicit record and any future durable history index, comparison surface, validation executor, or patch workflow.

## Listing records

The list command performs a non-recursive scan of `.ai/run-history/`, considers only direct `.json` files, sorts records by filename for deterministic output, and summarizes up to `--max-records` entries. It does not write an index, run validation commands, inspect diffs, read changed-file contents, generate patches, approve exceptions, enforce policy decisions, commit, push, call networks, or read environment variables.

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

## Selecting the latest readable record

The latest selector performs the same narrow direct-file scan but returns one selected record. Its ordering is explicit: records are considered by ascending filename, and the latest record is the last readable direct `.json` file by filename. Malformed or unsupported records are reported as refused and are not selected as latest.

```bash
forge run-history-latest --root .
```

For deterministic JSON output:

```bash
forge run-history-latest \
  --root . \
  --format json
```

## Safety checks

The history commands keep the surface narrow:

- They only look in `.ai/run-history/` below the supplied repository root.
- They scan only direct child files, not nested directories.
- They ignore non-JSON files.
- They reuse the single-record reader schema summary for each JSON record.
- They mark malformed or unsupported JSON records as `refused` instead of failing the whole list or latest selection.
- `run-history-list` refuses `--max-records` values lower than one.
- `run-history-latest` reports `latest_record: null` when no readable record exists.

## Summary fields

The list text and JSON summaries include:

- history directory path and status;
- records found, records listed, valid records, and refused records;
- each listed record path;
- readable/refused status;
- selected task identity when available;
- review status;
- preflight overall status;
- commit field;
- refusal reason for malformed or unsupported records.

The latest text and JSON summaries include:

- history directory path and status;
- the deterministic filename ordering rule;
- records found, readable records, and refused records;
- the selected latest readable record, or `none`/`null`;
- refused-record paths and reasons.

## Current limitations

These commands are intentionally history-inspection previews, not durable index writers. They do not compare records, verify commits, check workflow status, inspect repository settings, run tests, infer success, mutate `.ai/run-history/`, persist aggregate state, generate patches, inspect diffs, or enforce policy decisions.
