# Patch application preflight

`forge patch-application-preflight` is a read-only advisory gate that checks whether ready patch-text review evidence has explicit patch provenance metadata for every reviewed path before any future patch-application design relies on it.

It consumes only:

- one `forge patch-text-review --format json` output inside the configured root;
- repeated `--path` values;
- repeated `--patch-source` labels; and
- repeated `--expected-summary` values that must match the reviewed patch summaries.

Example:

```bash
forge patch-application-preflight \
  --root . \
  --review patch-text-review.json \
  --path README.md \
  --patch-source manual-review-note \
  --expected-summary "Review the intended README patch text." \
  --require-ready \
  --format json
```

The command returns `preflight_status=ready` only when the patch text review is ready, patch text review allowance is true, every reviewed path has exactly one provenance entry, no extra provenance path is supplied, every source label is explicit and non-empty, every expected summary is non-empty, and each expected summary exactly matches the reviewed summary for that path.

`patch_application_allowed` is always `false`. This command does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow status, approve implementation, mutate history, commit, push, or change files. `--require-ready` only changes the process exit code.
