# Validation Result Previews

`forge validation-result-preview` is a read-only bridge between saved run-history records and future validation-result persistence.

It accepts one explicit `.ai/run-history/*.json` record path plus one supplied validation result and prints the attachment that would be written later, without changing the record.

## Usage

```bash
forge validation-result-preview \
  --root . \
  --record .ai/run-history/latest.json \
  --result passed \
  --note "pytest passed" \
  --format json
```

Allowed `--result` values are:

- `passed`
- `failed`
- `error`
- `not_run`
- `skipped`

## Output

The command reports:

- the source record path;
- the selected task from the saved record;
- the current validation execution and result stored in the record;
- the commit field currently stored in the record;
- the proposed `validation_execution`, `validation_result`, and `validation_note` values;
- any blockers; and
- the safety boundary.

## Safety boundary

This command does not write files, rewrite run-history records, run validation commands, check workflow status, verify commits, inspect diffs, generate patches, infer success beyond the supplied result value, or enforce policy decisions.

It is intentionally a preview surface. A future writer can reuse this contract only after explicit persistence gates, path constraints, and tests exist.
