# Validation-result audits

`validation-result-audit` is a read-only CLI command and package helper for inspecting one saved `.ai/run-history/*.json` record after a validation result has been attached.

It exists between durable validation-result persistence and any future patch or diff workflow. Before a later tool trusts a saved validation observation, this command makes the record's validation fields explicit and checks whether they are internally consistent.

## CLI use

```bash
forge validation-result-audit \
  --root . \
  --record .ai/run-history/latest.json \
  --format json
```

The command exits with `0` when the audit is produced and exits with `2` when the record is missing, malformed, outside `.ai/run-history/`, or otherwise unsafe to inspect.

## What it reports

The audit returns stable text or JSON with:

- the source run-history record path;
- the selected task identity from the saved record;
- `validation_execution`, `validation_result`, and `validation_note`;
- the allowed validation-result values;
- a guard status of `consistent` or `needs-review`;
- guard notes explaining the status;
- the persistence label from the saved record; and
- a safety boundary.

## Guard rules

The audit is intentionally conservative:

- `validation_result` must be one of the allowed validation-result values.
- `not_run` results should keep `validation_execution=not_run` and should not carry a success/failure note.
- attached results such as `passed`, `failed`, or `skipped` should use `validation_execution=external_result_attached`.
- attached results should include a human-readable validation note.

The guard is advisory. It does not approve changes, enforce policy, or infer success beyond the saved JSON fields.

## Programmatic use

```python
from pathlib import Path

from autonomous_forge.validation_result_audit import read_validation_result_audit

print(
    read_validation_result_audit(
        Path(".ai/run-history/latest.json"),
        root=Path("."),
        output_format="json",
    )
)
```

## Safety boundary

The audit does not change files, run validation commands, check GitHub Actions or other workflow status, inspect diffs, read patch contents, generate patches, commit, push, call networks, or mark a task as approved. It only summarizes validation-result fields already saved in one path-validated local run-history record.
