# Run-history reads

`forge run-history-read` reads and summarizes one persisted local run-history JSON record. It is a read-only companion to `forge run-history-write` and also discovers immutable validation-result sidecars created by `forge validation-result-attachment-write`.

The command reads the explicit JSON file supplied by `--record` through a fixed **1 MiB ceiling**, then performs one bounded, non-recursive scan of `.ai/run-history/validation-attachments/`. It only verifies and surfaces attachments whose `source_record.path` explicitly names the selected record. It does not mutate the source record, run validation commands, inspect diffs, generate patches, approve exceptions, commit, push, call networks, or read environment variables.

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

If a verified immutable validation sidecar is bound to the selected record, text output lists it under `Immutable validation attachments`, while JSON output returns it in `validation_attachments`. Legacy `record.validation_result` and `record.validation_execution` fields are preserved exactly; attachments are additional evidence rather than an in-place schema rewrite.

## Safety checks

The reader refuses to summarize a record unless all of these are true:

- The record path stays inside the repository root.
- The record path is under `.ai/run-history/`.
- The record path uses a `.json` extension.
- The record is a real file, not a symlink.
- The record is a file, not a directory.
- The authoritative record is at most **1 MiB**; Forge reads at most one sentinel byte beyond the limit before refusing it.
- The record is valid UTF-8 JSON using the supported `run-history/v1` schema.
- The core `record`, `record.task`, and `preflight_summary` fields are JSON objects.
- If present, `record.validation_context` is a JSON object.
- The validation-attachment directory, when present, is a real directory rather than a symlink.
- Attachment discovery is bounded to at most 100 non-recursive `.json` candidates and 1,000 total direct directory entries.
- Each admitted validation attachment is read through a 1 MiB ceiling.
- Every matching `validation-attachment/v1` sidecar still matches the selected source record's exact SHA-256 and byte count.

Malformed or unrelated sidecar files are ignored unless they explicitly claim the selected source record; a matching attachment that fails verification blocks the read instead of being silently accepted.

## Summary fields

The text and JSON summaries include:

- source path;
- top-level and nested record schema versions;
- selected task identity and status before the run;
- review status and attention flag;
- legacy validation execution/result fields;
- retained validation context fields when present: `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register`;
- verified immutable validation attachments bound to the selected record;
- changed-files summary and commit field;
- preflight pass/warn/block summary;
- persistence mode;
- blockers;
- safety notes.

## Current limitations

The 1 MiB authoritative-record and attachment ceilings are fixed local fail-closed contracts rather than streaming validation. Attachment discovery is intentionally bounded and non-recursive. The reader surfaces immutable sidecars but does not collapse multiple observations into one inferred validation result, does not rewrite `run-history/v1`, and does not make replay/maintenance-bundle consumers treat an attachment as equivalent to executor-produced validation evidence. That separation keeps legacy consumers compatible while making the immutable evidence visible and verifiable through the primary history-reading path.
