# Patch text preflight

`forge patch-text-preflight` is a read-only gate between a draft-ready patch proposal preview and any future patch-text review surface.

It consumes two things only:

1. A `forge patch-proposal-draft --format json` output file.
2. Explicit per-path patch metadata supplied on the command line with matching `--path` and `--change-summary` entries.

Example:

```bash
forge patch-text-preflight \
  --root . \
  --draft patch-proposal-draft.json \
  --path README.md \
  --change-summary "Document the new command." \
  --require-ready \
  --format json
```

The command resolves, reads, and validates the supplied draft evidence once per invocation. Text output and `--require-ready` exit-code behavior are derived from that same in-memory preflight data so one invocation cannot accidentally format one draft state and gate a later draft state.

The command returns `preflight_status=ready` only when draft evidence is draft-ready, patch-draft work is allowed by that evidence, every draft target has explicit metadata, no extra metadata paths are introduced, validation steps are present, and all supplied path labels are safe repository-relative labels.

The command does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow status, approve implementation, mutate saved history, commit, push, or change files.
