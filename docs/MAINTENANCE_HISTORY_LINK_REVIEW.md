# Maintenance history link review

`forge maintenance-history-link-review` reviews one persisted `.ai/run-history` maintenance bundle link before a maintainer uses it for deeper bundle replay verification.

The command is local-first and read-only. It reads one repository-local JSON pointer, validates the history-link schema, and reports whether the pointer contains the durable information needed to continue the maintenance evidence workflow. When `--verify-linked-bundle` is supplied, it also reads the repository-local bundle referenced by the pointer, verifies the bundle SHA-256 against the pointer, and runs the existing maintenance replay summary so pointer review and hash-linked replay can happen in one command.

## Example

```bash
forge maintenance-history-link-review \
  --link .ai/run-history/AUTO-120-link.json \
  --require-ready
```

Verify the linked bundle and require replayable evidence:

```bash
forge maintenance-history-link-review \
  --link .ai/run-history/AUTO-120-link.json \
  --verify-linked-bundle \
  --require-linked-replayable
```

For machine-readable output:

```bash
forge maintenance-history-link-review \
  --link .ai/run-history/AUTO-120-link.json \
  --verify-linked-bundle \
  --format json
```

## Quality gates

The pointer-level review reports compact pass/fail/advisory gates for:

- confirmed history-link write status;
- bundle path and bundle SHA-256 pointer;
- reviewed paths;
- validation steps;
- required source-report stage pointers;
- retained validation context.

Missing retained validation context is advisory so older links can still be reviewed, while missing bundle/source/report information blocks readiness.

## Linked bundle replay

With `--verify-linked-bundle`, the command performs the next replay step only after the history link passes required pointer gates. It:

1. constrains the linked bundle path to the configured repository root;
2. recomputes the linked bundle SHA-256 and compares it with `bundle_sha256` from the history link;
3. runs `maintenance-replay-summary` against the linked bundle;
4. surfaces replay status, replay policy gate counts, source-report summary, validation-context consistency, and linked replay blockers in the same text/JSON output.

`--require-linked-replayable` returns exit code 2 unless linked-bundle verification was requested and the replay summary reports replayable evidence.

## Safety boundary

The command does not apply patches, run validation commands, stage files, create commits, push, change remotes, change branch protections, rerun workflows, or read environment variables. Linked-bundle verification reads only the repository-local bundle and source reports needed by maintenance replay summary, recomputes recorded hashes, and summarizes persisted JSON evidence.
