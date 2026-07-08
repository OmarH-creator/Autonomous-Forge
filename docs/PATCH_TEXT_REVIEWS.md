# Patch Text Reviews

`forge patch-text-review` is a read-only review gate between patch text preflight evidence and any future patch-text generation or apply workflow.

It consumes one ready `forge patch-text-preflight --format json` output plus explicit maintainer-supplied `--path` / `--patch-summary` pairs. It verifies that the reviewed paths exactly match the preflight target paths, that each summary is non-empty, that validation steps are still present, and that path labels remain safe repository-relative labels.

## Example

```bash
forge patch-text-review \
  --root . \
  --preflight patch-text-preflight.json \
  --path README.md \
  --patch-summary "Review README patch text intent before implementation." \
  --require-ready \
  --format json
```

## Safety boundary

The command reads supplied patch-text-preflight JSON and explicit summary metadata only. It does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow status, approve implementation, mutate saved history, commit, push, or change files.

`--require-ready` only changes the process exit code. A ready result is advisory process evidence, not implementation approval.
