# Executor handoff persistence

Executor handoff persistence is the guarded bridge between `forge executor-run --format json` and the existing validation-result writer.

It consumes a reviewed executor-run JSON payload, validates the `persistence_handoff` object, and persists the observed result only through the same path guards used by `forge validation-result-write`.

## CLI usage

```bash
forge executor-run \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --command "python -m pytest" \
  --confirm-executor-dry-run \
  --format json > executor-run-output.json

forge executor-handoff-persist \
  --root . \
  --executor-output executor-run-output.json \
  --confirm-write \
  --format json
```

The command is intentionally separate from `forge executor-run`. Maintainers must review the executor output first, then run `executor-handoff-persist` only when the observed result should be written into the saved run-history record named by the handoff.

## Read-only preview helper

`read_executor_handoff_persistence_preview()` summarizes the same handoff payload without writing anything. It reports the executor-output path, target record, validation execution value that would be persisted, validation result, note, confirmation requirement, derived write command, and safety boundary in text or JSON.

This preview is useful between `executor-run --format json` and the confirmed persistence command when a caller wants a review artifact showing exactly what the persistence step would do before mutating the run-history record.

## Implemented behavior

The helper and CLI accept one executor-run JSON file and check that:

- the executor-output file is a real `.json` file inside the repository root, not a symlink, directory, missing file, or external path;
- `persistence_handoff.available` is `true`;
- `persistence_handoff.auto_persistence` is `false`;
- `persistence_handoff.confirmation_required` is `--confirm-write`;
- the handoff record is a non-empty `.ai/run-history/*.json` target accepted by the validation-result writer;
- the handoff validation result is in the supported validation-result vocabulary;
- the executor output result matches the handoff result;
- the executor output result-record path, when present, matches the handoff record.

The preview builder returns the exact payload that would be written without mutating files. The read-only preview helper returns a concise review summary derived from that payload. The writer and CLI require explicit confirmation and then delegate to the validation-result writer so existing path and record-shape checks remain the source of truth.

## Safety boundary

Executor handoff persistence does not run validation commands, rerun executor output, poll GitHub workflows, infer success, inspect diffs, generate patches, enforce policy, commit, push, or automatically mutate history. It persists only a supplied, already-observed executor result after explicit confirmation.

## Example programmatic flow

```python
from pathlib import Path

from autonomous_forge.executor_handoff_persistence import (
    read_executor_handoff_persistence_preview,
    write_executor_handoff_persistence,
)

preview = read_executor_handoff_persistence_preview(
    Path("executor-run-output.json"),
    root=Path("."),
    output_format="json",
)
print(preview)

summary = write_executor_handoff_persistence(
    Path("executor-run-output.json"),
    root=Path("."),
    confirm_write=True,
)
print(summary["validation_result"])
```

Keep the executor run and persistence steps separate. Review the executor output first, optionally render the read-only preview, then persist the handoff only when the observed result should become durable local history.
