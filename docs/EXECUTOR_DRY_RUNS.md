# Validation Executor Dry-Run Previews

`forge executor-dry-run` checks one exact executor-contract candidate command and reports whether a future executor would be ready to run it. The command is still read-only and never starts a subprocess.

## Usage

```bash
forge executor-dry-run \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --command "python -m pytest" \
  --confirm-executor-dry-run
```

For machine-readable review:

```bash
forge executor-dry-run \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --command "python -m pytest" \
  --confirm-executor-dry-run \
  --format json
```

## What it checks

The preview reports:

- selected roadmap task context;
- requested command string;
- whether `--confirm-executor-dry-run` was supplied;
- whether the command exactly matches an executor-contract candidate;
- whether the upstream contract and gate are eligible;
- conservative shell-syntax blockers;
- simulated execution metadata with `planned-not-run` or `blocked-not-run` status;
- result-record path and fields a future executor would have to update through `forge validation-result-write`.

## Safety boundary

The dry-run preview does not run commands, create subprocesses, poll workflows, verify commits, inspect diffs, read changed-file contents, generate patches, grant approval, infer validation success, enforce policy, or mutate saved history. It is a reviewable final check before any real validation executor is implemented.
