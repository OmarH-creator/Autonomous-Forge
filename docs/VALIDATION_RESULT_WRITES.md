# Validation Result Writes

`forge validation-result-write` is the narrow persistence step after `forge validation-result-preview`.

It attaches one explicitly supplied validation result to one saved run-history record under `.ai/run-history/`.

## Safety contract

The command and writer:

- require explicit confirmation through `--confirm-write` on the CLI or `confirm_write=True` through the Python API;
- accept only validation results already supported by the preview surface: `passed`, `failed`, `error`, `not_run`, and `skipped`;
- reuse the run-history reader path guard, so the target must be a real non-symlink `.json` file under `.ai/run-history/`;
- read the authoritative source record through a fixed 1 MiB ceiling before decoding, parsing, payload construction, stale-source comparison, or replacement;
- refuse malformed records, invalid UTF-8, oversized records, and unsupported schemas through the writer/preview/reader path;
- update the record validation fields from a supplied external observation only when the record does not already contain validation evidence;
- treat the historical `run-history/v1` placeholder spelling `not run` and the newer `not_run` spelling as equivalent empty validation states, so legacy records can receive their first explicitly confirmed attachment without weakening immutability for real evidence;
- refuse to replace an existing validation execution, result, or note, including executor-produced evidence or an earlier external attachment;
- re-read the source through the same 1 MiB ceiling immediately before replacement and refuse a stale or newly oversized attachment if another writer changed or grew the record while the payload was being prepared;
- persist the first attachment through a flushed same-directory temporary file followed by `os.replace`, so a failed final replacement leaves the original durable record intact instead of exposing a partially written JSON file;
- fsync the containing directory after the successful replacement so the rename metadata is pushed toward durable storage on supported platforms/filesystems;
- if that post-replace directory sync fails, SHA-256 check that the current record still matches the exact replacement bytes from this invocation, then restore the exact pre-write bytes through another flushed same-directory temporary file and fsync the directory again;
- refuse to restore over a record that changed after replacement, preserving those bytes for inspection instead of risking deletion or overwrite of another writer's data;
- clean up replacement and rollback temporary files on handled failures;
- retain implementation-grade context fields already present on the record in `record.validation_context`, including `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register`;
- do not run validation commands, check workflow status, verify commits, inspect diffs, generate patches, infer success, enforce policy, commit, push, call networks, or scan history recursively.

Validation evidence is single-assignment through this writer. After a result has been recorded, a later observation must use a new run-history record or a separately reviewed recovery mechanism; rerunning this command against the same validated record fails closed and preserves its bytes.

The 1 MiB source ceiling is deliberately the same fixed local bound used by the primary `run-history-read` path and immutable validation-attachment inputs. The writer reads at most one sentinel byte beyond the ceiling and fails before JSON parsing or replacement if that sentinel exists. The ceiling is reapplied at the final stale-source check, so a record that grows after payload construction is not allowed to become an unbounded final read.

The write is crash/failure resistant at the replacement boundary: Forge fully writes and flushes a temporary sibling file first, atomically replaces the target, and then fsyncs the containing directory. If replacement itself fails, the existing history record is preserved and the temporary file is removed. If directory fsync fails after replacement, Forge now treats that as a failed publication and attempts to restore the exact original bytes. Restoration is ownership-checked twice against the SHA-256 of the replacement before the rollback `os.replace`; if the target no longer matches, Forge preserves the changed record and fails closed. After restoration Forge fsyncs the directory again. This narrows the ambiguity that previously left a newly replaced authoritative record behind after a durability error.

Forge does not implement a shared cross-process lock. The pre-replacement byte comparison and rollback ownership checks narrow concurrent-writer races but do not claim full multi-process transactional locking. A process/host failure that prevents Python cleanup, a second directory-sync failure during rollback, or a target change in the tiny interval between the final ownership check and rollback rename can still require manual inspection.

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

If `--confirm-write` is omitted, the command returns exit code `2`, prints a refusal, and does not mutate the target record. If the record already contains validation evidence, the write is also refused and the existing record remains unchanged. If the record changes or grows beyond 1 MiB between the initial read and the final replacement, Forge refuses the stale attachment rather than replacing the newer bytes.

If the replacement succeeds but its parent-directory durability sync fails, the command returns an error. When the replacement bytes are still owned by this invocation, the original record is restored before that error is returned. When the current bytes no longer match the replacement digest, Forge leaves them untouched and explicitly reports that the changed record was preserved for inspection.

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
