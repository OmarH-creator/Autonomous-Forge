# Guarded Patch Apply

`forge patch-apply` is the first intentionally write-capable patch command in Autonomous Forge. It overwrites exactly one repository-local target file with one explicit replacement-text file, but only after the generated patch preview and change-readiness evidence both match the current local inputs.

The command is deliberately narrow:

- it requires `--confirm-apply`;
- it consumes `forge patch-generation-preview --format json` output;
- it consumes `forge change-readiness --format json` output;
- the target path must match the generated preview and appear in change-readiness evidence;
- the current target file plus replacement file must reproduce the supplied patch preview exactly;
- the replacement file must be UTF-8, repository-local, non-symlinked, under 1 MB, and free of simple blocked secret-marker strings;
- it writes only the requested target file and never commits, pushes, calls networks, reads environment variables, mutates saved history, or runs validation commands.

## Example

```bash
forge patch-apply \
  --root . \
  --preview patch-generation-preview.json \
  --change-readiness change-readiness.json \
  --path README.md \
  --replacement README.replacement.md \
  --confirm-apply \
  --require-applied \
  --format json
```

After the command reports `file_changed: true`, run the listed validation steps and review the resulting git diff before committing.

## Why this is separate from patch generation

`forge patch-generation-preview` creates reviewable unified diff text but does not mutate files. `forge patch-apply` is intentionally a separate, explicitly confirmed step so generated text, diff/status evidence, and the final local file write remain auditable.
