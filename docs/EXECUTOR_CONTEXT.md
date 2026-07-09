# Executor Context Propagation

AUTO-113 extends the implementation-grade planning context beyond validation orchestration into the executor handoff chain.

## Purpose

`forge plan`, `forge propose`, `forge validate-plan`, `forge validation-preview`, and `forge validation-orchestration` already preserve these structured fields:

- `expected_file_changes`
- `implementation_steps`
- `validation_steps`
- `risk_register`

AUTO-113 carries those same fields into:

- `forge command-execution-handoff`
- `forge executor-gate`
- `forge executor-contract`
- `forge executor-dry-run`

This keeps executor review tied to the actual implementation objective instead of reducing the handoff to only command candidates, confirmation flags, and saved-history paths.

## Safety boundary

The enriched fields are review context only. They do not grant approval, run validation, inspect diffs, generate patches, mutate files, stage commits, push branches, call networks, or enforce policy.

`forge executor-run` remains the only narrow validation-execution path in this part of the workflow, and it still requires an exact gated command plus explicit confirmation.

## Expected review flow

```bash
forge command-execution-handoff --format json
forge executor-gate --format json
forge executor-contract --format json
forge executor-dry-run --command "python -m pytest" --confirm-executor-dry-run --format json
```

Reviewers should confirm that the selected command matches the validation steps and that the risk register does not require broader human approval before running a confirmed executor command.
