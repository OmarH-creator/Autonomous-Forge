# Validation Result Writes

`forge validation-result-write` is the narrow persistence step after `forge validation-result-preview`.

It attaches one explicitly supplied validation result to one saved run-history record under `.ai/run-history/`.

## Safety contract

The command and writer:

- require explicit confirmation through `--confirm-write` on the CLI or `confirm_write=True` through the Python API;
- accept only validation results already supported by the preview surface: `passed`, `failed`, `error`, `not_run`, and `skipped`;
- reuse the run-history reader path guard, so the target must be a real non-symlink `.json` file under `.ai/run-history/`;
- refuse malformed records and unsupported schemas through the preview/reader path;
- update the record validation fields from a supplied external observation only when the record does not already contain validation evidence;
- refuse to replace an existing validation execution, result, or note, including executor-produced evidence or an earlier external attachment;
- re-check the source record bytes immediately before replacement and refuse a stale attachment if another writer changed the record while the payload was being prepared;
- persist the first attachment through a flushed same-directory temporary file followed by `os.replace`, so a failed final replacement leaves the original durable record intact instead of exposing a partially written JSON file;
- clean up its temporary file when the atomic replacement fails;
- retain implementation-grade context fields already present on the record in `record.validation_context`, including `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register`;
- do not run validation commands, check workflow status, verify commits, inspect diffs, generate patches, infer success, enforce policy, commit, push, call networks, or scan history recursively.

Validation evidence is single-assignment through this writer. After a result has been recorded, a later observation must use a new run-history record or a separately reviewed recovery mechanism; rerunning this command against the same validated record fails closed and preserves its bytes.

The write is also crash/failure resistant at the final file-replacement boundary: Forge fully writes and flushes a temporary sibling file first, then replaces the target atomically. If that replacement fails, the existing history record is preserved and the temporary file is removed. Forge does not implement a shared cross-process lock, so the pre-replacement byte comparison narrows concurrent-writer races but does not claim full multi-process transactional locking.

## CLI

```bash
forge validation-result-write \
  --root . \
  --record .ai/run-history/latest.json \
  --result passed \
  --note "pytest passed locally" \
  --confirm-write
```

Successful text output includes:

```text
Validation-result attachment written: <path>
Validation execution: external_result_attached
Validation result: passed
Validation note: pytest passed locally
```

Use `--format json` when automation needs a stable machine-readable summary of the write without scraping text output:

```bash
forge validation-result-write \
  --root . \
  --record .ai/run-history/latest.json \
  --result failed \
  --note "pytest failed locally" \
  --confirm-write \
  --format json
```

```json
{
  "path": ".ai/run-history/latest.json",
  "validation_execution": "external_result_attached",
  "validation_note": "pytest failed locally",
  "validation_result": "failed"
}
```

If `--confirm-write` is omitted, the command returns exit code `2`, prints a refusal, and does not mutate the target record. If the record already contains validation evidence, the write is also refused and the existing record remains unchanged. If the record changes between the initial read and the final replacement, Forge refuses the stale attachment rather than replacing the newer bytes.

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

When the source record already contains implementation context, the Python result includes `validation_context` and `validation_context_retained`, and the saved record receives the same context under `record.validation_context`.

## Persisted fields

On the first successful attachment, the writer updates:

- `record.validation_execution`
- `record.validation_result`
- `record.validation_note`
- `record.validation_context`, when implementation context exists on the source record
- top-level `validation_context_retained`
- top-level `persistence`
- `safety_notes`, with an additional note that the result was supplied externally and, when applicable, that implementation context was retained

This is intentionally smaller than a validation executor. It records an already-observed result; it does not create or verify that result, and it does not replace previously recorded validation evidence.
