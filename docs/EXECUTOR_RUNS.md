# Opt-In Validation Executor Runs

`forge executor-run` is the first narrow command that can execute a local validation command. It is intentionally limited to one exact command candidate that already appears in the executor contract and passes the dry-run gate.

## Usage

```bash
forge executor-run \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --command "python -m pytest" \
  --confirm-executor-dry-run
```

For machine-readable output:

```bash
forge executor-run \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --command "python -m pytest" \
  --confirm-executor-dry-run \
  --format json
```

## What it does

The executor run:

- rebuilds the executor-contract and dry-run decision from local repository files;
- refuses missing confirmation, unknown commands, shell-control syntax, redirection, command expansion, and multiline input;
- accepts only an exact executor-contract candidate such as `python -m pytest`;
- invokes `subprocess.run` with `shell=false`;
- uses the repository root as the command working directory;
- applies a fixed 300-second timeout;
- captures bounded stdout and stderr summaries;
- reports the observed return code and maps it to `validation_result=passed` or `validation_result=failed`;
- leaves persistence to a later explicit `forge validation-result-write --confirm-write` call.

## Safety boundary

`forge executor-run` is a validation runner, not a general automation runner. It does not run arbitrary commands, use a shell, poll workflows, call networks, verify commits, inspect diffs, read changed-file contents, generate patches, enforce policy, commit, push, or mutate saved history. It reports observed local validation output only.
