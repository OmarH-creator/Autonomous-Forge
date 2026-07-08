# Validation Executor Contract Previews

`forge executor-contract` defines the narrow contract a future opt-in validation executor must satisfy before any command-running implementation is added.

The command is read-only. It consumes the existing executor precondition gate and turns that gate into explicit future executor requirements, refusal cases, timeout policy, and result-capture shape.

## Usage

```bash
forge executor-contract \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

For machine-readable review:

```bash
forge executor-contract \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

## Contract fields

The preview reports:

- selected roadmap task context;
- upstream executor-gate status;
- `future_confirmation_flag`, currently `--confirm-executor-dry-run`;
- `executor_dry_run_allowed_now=false` because this command never executes validations;
- allowed future command classes;
- exact candidate commands inherited from the gate;
- refusal cases that a later executor must enforce;
- validation result fields that must be captured through `forge validation-result-write --confirm-write`;
- timeout defaults and upper bound;
- future required inputs;
- non-goals and safety boundary.

## Safety boundary

The contract preview does not run commands, poll workflows, verify commits, inspect diffs, read changed-file contents, generate patches, grant approval, infer validation success, enforce policy, or mutate saved history.

A future executor remains out of scope until this contract is stable and deliberately implemented in a separate task.
