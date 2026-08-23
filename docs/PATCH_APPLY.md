# Guarded Patch Apply

`forge patch-apply` is the first intentionally write-capable patch command in Autonomous Forge. It replaces exactly one repository-local target file with one explicit replacement-text file, but only after the generated patch preview and change-readiness evidence both match the current local inputs.

The command is deliberately narrow:

- it requires `--confirm-apply` before any file can be changed;
- it consumes `forge patch-generation-preview --format json` output;
- it consumes `forge change-readiness --format json` output;
- the target path must match the generated preview and appear in change-readiness evidence;
- the current target file plus replacement file must reproduce the supplied patch preview exactly;
- the replacement file must be UTF-8, repository-local, non-symlinked, under 1 MB, and free of simple blocked secret-marker strings;
- it writes only the requested target file and never commits, pushes, calls networks, reads environment variables, mutates saved history, or runs validation commands.

## Atomic target replacement

Confirmed writes are prepared in a same-directory temporary file. Forge preserves the target's permission mode, flushes and `fsync`s the complete replacement, then uses `os.replace` to atomically switch the target path to the prepared file and `fsync`s the containing directory.

This prevents an interrupted write from exposing a partially truncated working file. If replacement fails before `os.replace`, the original target remains intact and the temporary file is cleaned up. If the atomic replacement succeeds but the parent-directory durability sync fails, Forge reports that the replacement has already occurred and requires inspection before retrying instead of falsely claiming the original file survived.

## Optional live-diff verification

Pass `--verify-live-diff` to connect the write step to the live tracked-diff capability added in AUTO-143. After the atomic replacement is written, Forge runs a bounded target-scoped command equivalent to:

```text
git diff --no-ext-diff --no-textconv HEAD -- <target-path>
```

The pathspec is validated as a repository-relative path and the subprocess uses `shell=False`, a 15-second timeout, and the existing 1 MB diff bound. The resulting unified diff is reviewed against the repository policy supplied through `--policy` (default `.forge/policy.md`). Verification succeeds only when the live diff is clear, contains exactly one changed file, and reviews exactly the requested target path.

If git execution, decoding, bounds, parsing, policy review, file-count, or target-path verification fails, Forge atomically restores the original target contents using the same durable replacement path and exits with a refusal. If that rollback itself fails, Forge reports the rollback failure explicitly and requires the target to be inspected before retrying.

This gate covers tracked diff evidence only. It does not inspect untracked files, run tests, prove correctness, commit, or push.

## Exit-code behavior

By default, the command returns a report even when the apply step is blocked by missing confirmation or stale evidence. This lets a maintainer inspect why a write would not occur without treating the report itself as a command failure.

Use `--require-applied` when automation should fail closed unless `file_changed` is true. A failed `--verify-live-diff` check always returns a refusal because the write is rolled back when rollback succeeds.

## Example

```bash
forge patch-apply \
  --root . \
  --preview patch-generation-preview.json \
  --change-readiness change-readiness.json \
  --path README.md \
  --replacement README.replacement.md \
  --confirm-apply \
  --verify-live-diff \
  --policy .forge/policy.md \
  --require-applied \
  --format json
```

A successful JSON result reports `file_changed: true`, `live_diff_verified: true`, and includes the target-scoped `live_diff_review` evidence. Run the listed validation steps before committing.

## Why this is separate from patch generation

`forge patch-generation-preview` creates reviewable unified diff text but does not mutate files. `forge patch-apply` is intentionally a separate, explicitly confirmed step so generated text, diff/status evidence, the final local file write, and optional post-write diff verification remain auditable.
