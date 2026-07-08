# Command-execution handoff previews

`forge command-execution-handoff` builds a local, read-only handoff artifact for a future controlled validation executor.

The command consumes the same planning inputs as the other policy-aware commands:

```bash
forge command-execution-handoff \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

## What it reports

The preview includes:

- the selected roadmap task;
- the validation orchestration status;
- eligible command candidates copied from the conservative validation-preview allowlist;
- candidates that still require review;
- blockers from orchestration readiness and saved-history validation guards;
- required human confirmations before any future executor could run a command;
- the expected saved-history record fields that a separate validation-result write might update later.

## Safety boundary

The command is intentionally advisory. It does not run validation commands, poll workflow status, verify commits, change files, inspect diffs, generate patches, grant approval, infer validation success, enforce policy, or attach validation results.

Only the existing explicit history-write commands mutate local `.ai/run-history/*.json` files, and those still require their own confirmation flags.
