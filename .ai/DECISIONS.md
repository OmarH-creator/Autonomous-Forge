# Autonomous Decisions

## DEC-046 — 2026-07-08 — Permit one narrow opt-in local validation executor

Context: `forge executor-dry-run` proved that one requested command could match the executor contract, but the product still could not perform the local validation step needed for an end-to-end maintenance workflow.
Decision: Add `forge executor-run --format text|json` as a narrow opt-in executor. It accepts only one exact executor-contract candidate, requires `--confirm-executor-dry-run`, refuses shell-control syntax and unknown commands, runs with `subprocess.run(..., shell=false)`, applies a fixed timeout, captures bounded output, and reports the observed return code/result without mutating saved history.
Alternatives considered: Keep the product permanently review-only, run arbitrary commands, use a shell, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, mutate history automatically, or combine execution and persistence in one command.
Consequences: Autonomous Forge can now perform a controlled local validation command while preserving explicit confirmation, no-shell execution, bounded output, and separate result persistence. This is still not a general automation runner.
Human decision still required: No.

## DEC-045 — 2026-07-08 — Dry-run executor candidates before real execution

Context: `forge executor-contract` defined future executor requirements, but there was no user-facing way to test one requested command against that contract before implementing command execution.
Decision: Add `forge executor-dry-run --format text|json` as a read-only dry-run preview. It accepts one exact command candidate, requires `--confirm-executor-dry-run`, blocks shell-control syntax and unknown commands, and emits simulated execution/result-record metadata while keeping `command_execution_allowed=false`.
Alternatives considered: Move directly to a subprocess executor, run arbitrary commands, rely only on the contract document, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, or mutate history automatically.
Consequences: Maintainers can now review whether a specific validation command would pass the gate/contract chain before any real execution behavior exists. The command remains advisory and does not run validations, prove success, or approve execution.
Human decision still required: No.

## DEC-044 — 2026-07-08 — Define executor contract before command execution

Context: `forge executor-gate` exposed whether a future dry-run executor path was eligible for explicit future confirmation, but the exact contract for a later executor was still implicit.
Decision: Add `forge executor-contract --format text|json` as a read-only contract preview. The contract consumes executor-gate data and names the future `--confirm-executor-dry-run` flag, allowed command classes, refusal cases, result-capture shape, timeout policy, required future inputs, non-goals, and safety boundary while keeping `executor_dry_run_allowed_now=false`.
Alternatives considered: Move directly to a command runner, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, mutate history automatically, or leave executor behavior to undocumented future assumptions.
Consequences: Maintainers can now review the exact future executor requirements before any command-running behavior exists. The command remains advisory and does not run validations, prove success, or approve execution.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
