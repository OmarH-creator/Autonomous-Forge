# Executor Context Propagation

AUTO-114 extends the implementation-grade planning context through the executor run and validation-result persistence handoff.

## Purpose

`forge plan`, `forge propose`, `forge validate-plan`, `forge validation-preview`, `forge validation-orchestration`, `forge command-execution-handoff`, `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` already preserve these structured fields:

- `expected_file_changes`
- `implementation_steps`
- `validation_steps`
- `risk_register`

AUTO-114 carries those same fields into:

- `forge executor-run`
- the nested `persistence_handoff` object that points to the explicit `forge validation-result-write --confirm-write` command

This keeps observed local validation evidence tied to the actual implementation objective instead of reducing the handoff to only command text, return code, captured output, and result-record paths.

## Safety boundary

The enriched fields are review context only. They do not grant approval, run extra validation, inspect diffs, generate patches, mutate files, stage commits, push branches, call networks, or enforce policy.

`forge executor-run` remains the only narrow validation-execution path in this part of the workflow. It still requires an exact gated command plus explicit confirmation, executes with `shell=false`, and only prepares an advisory persistence handoff. It does not write validation-result history automatically.

## Expected review flow

```bash
forge command-execution-handoff --format json
forge executor-gate --format json
forge executor-contract --format json
forge executor-dry-run --command "python -m pytest" --confirm-executor-dry-run --format json
forge executor-run --command "python -m pytest" --confirm-executor-dry-run --format json
```

Reviewers should confirm that the selected command matches the validation steps, that the observed result is appropriate for the expected file changes, and that the risk register does not require broader human approval before running the explicit persistence command.