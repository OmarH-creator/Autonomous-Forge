# Validation Result Writes

`forge validation-result-write` is the narrow persistence step after `forge validation-result-preview`.

It attaches one explicitly supplied validation result to one saved run-history record under `.ai/run-history/`.

## Safety contract

The command and writer:

- require explicit confirmation through `--confirm-write` on the CLI or `confirm_write=True` through the Python API;
- accept only validation results already supported by the preview surface: `passed`, `failed`, `error`, `not_run`, and `skipped`;
- reuse the run-history reader path guard, so the target must be a real non-symlink `.json` file under `.ai/run-history/`;
- refuse malformed records and unsupported schemas through the preview/reader path;
- write only the selected run-history record;
- update the record validation fields from a supplied external observation;
- do not run validation commands, check workflow status, verify commits, inspect diffs, generate patches, infer success, enforce policy, commit, push, call networks, or scan history recursively.

## CLI

```bash
forge validation-result-write \
  --root . \
  --record .ai/run-history/latest.json \
  --result passed \
  --note "pytest passed locally" \
  --confirm-write
```

Successful output includes:

```text
Validation-result attachment written: <path>
Validation execution: external_result_attached
Validation result: passed
Validation note: pytest passed locally
```

If `--confirm-write` is omitted, the command returns exit code `2`, prints a refusal, and does not mutate the target record.

## Python API

```python
from pathlib import Path

from autonomous_forge.validation_result_writer import write_validation_result_attachment

write_validation_result_attachment(
    Path(".ai/run-history/latest.json"),
    result="passed",
    note="pytest passed locally",
    confirm_write=True,
)
```

## Persisted fields

The writer updates:

- `record.validation_execution`
- `record.validation_result`
- `record.validation_note`
- top-level `persistence`
- `safety_notes`, with an additional note that the result was supplied externally

This is intentionally smaller than a validation executor. It records an already-observed result; it does not create or verify that result.
