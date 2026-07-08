# Executor precondition gate previews

`forge executor-gate` builds a local, read-only precondition gate before any validation executor exists.

```bash
forge executor-gate \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

## What it reports

The preview includes:

- the selected roadmap task;
- the upstream command-execution handoff status;
- whether a future dry-run executor path is eligible for explicit confirmation;
- positive allow reasons when all conservative preconditions are clear;
- block reasons when command candidates, saved-history targets, or handoff readiness are missing;
- gated command candidates with `execution_status: not run`;
- required confirmations before any future executor could run a command;
- the saved run-history record path that a later validation-result write would target.

## Safety boundary

The command is intentionally advisory. It does not run validation commands, poll workflow status, verify commits, inspect diffs, read changed-file contents, generate patches, approve execution, infer validation success, enforce policy, mutate run-history records, commit, push, call networks, or read environment variables.

The gate can report that a future dry-run path is eligible only for explicit future confirmation. It still never grants approval or executes anything by itself.
