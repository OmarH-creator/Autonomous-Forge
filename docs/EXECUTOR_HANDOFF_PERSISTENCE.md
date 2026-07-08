# Executor handoff persistence

Executor handoff persistence is the guarded bridge between `forge executor-run --format json` and the existing validation-result writer.

It consumes a reviewed executor-run JSON payload, validates the `persistence_handoff` object, and persists the observed result only through the same path guards used by `forge validation-result-write`.

## Implemented behavior

The helper accepts one executor-run JSON file and checks that:

- the executor-output file is a real `.json` file inside the repository root, not a symlink, directory, missing file, or external path;
- `persistence_handoff.available` is `true`;
- `persistence_handoff.auto_persistence` is `false`;
- `persistence_handoff.confirmation_required` is `--confirm-write`;
- the handoff record is a non-empty `.ai/run-history/*.json` target accepted by the validation-result writer;
- the handoff validation result is in the supported validation-result vocabulary;
- the executor output result matches the handoff result;
- the executor output result-record path, when present, matches the handoff record.

The preview builder returns the exact payload that would be written without mutating files. The writer requires explicit confirmation and then delegates to the validation-result writer so existing path and record-shape checks remain the source of truth.

## Safety boundary

Executor handoff persistence does not run validation commands, rerun executor output, poll GitHub workflows, infer success, inspect diffs, generate patches, enforce policy, commit, push, or automatically mutate history. It persists only a supplied, already-observed executor result after explicit confirmation.

## Example programmatic flow

```python
from pathlib import Path

from autonomous_forge.executor_handoff_persistence import write_executor_handoff_persistence

summary = write_executor_handoff_persistence(
    Path("executor-run-output.json"),
    root=Path("."),
    confirm_write=True,
)
print(summary["validation_result"])
```

Keep the executor run and persistence steps separate. Review the executor output first, then persist the handoff only when the observed result should become durable local history.