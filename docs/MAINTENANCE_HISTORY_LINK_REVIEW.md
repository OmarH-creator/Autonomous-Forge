# Maintenance history link review

`forge maintenance-history-link-review` reviews one persisted `.ai/run-history` maintenance bundle link before a maintainer uses it for deeper bundle replay verification.

The command is local-first and read-only. It reads one repository-local JSON pointer, validates the history-link schema, and reports whether the pointer contains the durable information needed to continue the maintenance evidence workflow.

## Example

```bash
forge maintenance-history-link-review \
  --link .ai/run-history/AUTO-120-link.json \
  --require-ready
```

For machine-readable output:

```bash
forge maintenance-history-link-review \
  --link .ai/run-history/AUTO-120-link.json \
  --format json
```

## Quality gates

The review reports compact pass/fail/advisory gates for:

- confirmed history-link write status;
- bundle path and bundle SHA-256 pointer;
- reviewed paths;
- validation steps;
- required source-report stage pointers;
- retained validation context.

Missing retained validation context is advisory so older links can still be reviewed, while missing bundle/source/report information blocks readiness.

## Safety boundary

The command does not read the linked bundle, recompute hashes, run validation commands, stage files, create commits, push, change remotes, change branch protections, rerun workflows, or read environment variables. After a link is ready, run `forge maintenance-replay-summary --bundle <bundle.json>` to verify the linked bundle and source-report hashes.
