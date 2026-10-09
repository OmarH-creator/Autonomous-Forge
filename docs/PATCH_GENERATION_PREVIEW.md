# Patch Generation Preview

`forge patch-generation-preview` is the first guarded patch-text generation surface in Autonomous Forge. It consumes ready `forge patch-application-readiness --format json` evidence, one explicit repository target path, and one explicit UTF-8 replacement-text file, then prints a bounded unified diff preview.

It is intentionally not a patch applier. The command does not modify files, run commands, call networks, inspect environment variables, mutate saved history, commit, push, or mark the change approved. `patch_application_allowed` is always `false`.

## Example

```bash
forge patch-generation-preview \
  --root . \
  --readiness patch-application-readiness.json \
  --path README.md \
  --replacement README.replacement.md \
  --require-generated \
  --format json
```

## Readiness requirements

The readiness input must be a repository-local JSON object produced by `forge patch-application-readiness --format json`. The command only generates a preview when:

- `readiness_status` is `ready`;
- `patch_application_readiness_allowed` is `true`;
- `patch_application_allowed` remains `false`;
- the requested target path is listed in `reviewed_paths`;
- validation steps are present; and
- the replacement text differs from the current target content.

## Safety checks

The command refuses unsafe path labels, symlink inputs, files outside the configured root, non-regular files, non-UTF-8 text, oversized text, malformed readiness JSON, and text containing simple blocked secret-marker strings such as `secret`, `token`, `password`, `api_key`, or `private key`.

These marker checks are guardrails, not complete secret scanning. Review the generated patch text before using it anywhere else.

## Bounded input snapshots and strict exit gate

Readiness JSON, target text, and replacement text are each opened once in binary mode and read with a 1,000,001-byte sentinel. Inputs above 1,000,000 bytes are refused before UTF-8 decoding or JSON parsing. This prevents a file growing between a pre-read size check and an unbounded second read. The replacement file in the example must be under `--root` (it need not be tracked).

`--require-generated` checks the same preview object printed to stdout, without reopening any input. A blocked preview therefore exits `2` even if its input files change immediately after the preview was constructed. This does not lock files or authenticate readiness evidence; the separately confirmed patch applier still revalidates the target before writing.
