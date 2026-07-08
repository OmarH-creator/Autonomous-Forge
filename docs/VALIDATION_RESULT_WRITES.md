# Validation Result Writes

`validation_result_writer` is the narrow persistence step after `forge validation-result-preview`.

It attaches one explicitly supplied validation result to one saved run-history record under `.ai/run-history/`.

## Safety contract

The writer:

- requires an explicit `confirm_write=True` call;
- accepts only validation results already supported by the preview surface: `passed`, `failed`, `error`, `not_run`, and `skipped`;
- reuses the run-history reader path guard, so the target must be a real non-symlink `.json` file under `.ai/run-history/`;
- refuses malformed records and unsupported schemas through the preview/reader path;
- writes only the selected run-history record;
- updates the record validation fields from a supplied external observation;
- does not run validation commands, check workflow status, verify commits, inspect diffs, generate patches, infer success, enforce policy, commit, push, call networks, or scan history recursively.

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
