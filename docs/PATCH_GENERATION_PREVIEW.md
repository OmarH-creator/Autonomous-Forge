# Patch Generation Preview

`forge patch-generation-preview` is the first guarded patch-text generation surface in Autonomous Forge. It consumes ready `forge patch-application-readiness --format json` evidence, one explicit repository target path, and one explicit UTF-8 replacement-text file, then prints a bounded unified diff preview.

It is intentionally not a patch applier. The command does not modify files, run commands, call networks, inspect environment variables, mutate saved history, commit, push, or mark the change approved. `patch_application_allowed` is always `false`.

## Example

```bash
forge patch-generation-preview \
  --root . \
  --readiness patch-application-readiness.json \
  --path README.md \
  --replacement /tmp/README.replacement.md \
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
