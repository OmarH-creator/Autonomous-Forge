# Autonomous Decisions

## DEC-047 — 2026-07-08 — Treat executor launch failures and handoffs as structured observations

Context: `forge executor-run` handled completed and timed-out subprocesses, but OS-level startup failures such as a missing executable could still escape as unhandled CLI errors after the dry-run gate had approved the exact command. A concurrent executor-result persistence handoff also landed during the same maintenance window.
Decision: Catch `OSError` from the no-shell subprocess runner and report it as structured `execution_status=launch-failed`, `validation_execution=local_command_observed`, and `validation_result=failed` output with bounded stderr context and no return code. Preserve the concurrent persistence handoff as advisory output only: it may describe the exact `forge validation-result-write --confirm-write` command, but it must not write history automatically.
Alternatives considered: Let startup errors crash the CLI, treat missing executables as blocked before execution despite occurring after gate approval, silently mark them not-run, revert the handoff, persist automatically, or broaden command execution to recover automatically.
Consequences: Executor output remains machine-readable and durable-history-ready even when local runtime setup is broken, while preserving the same narrow command allowlist, no-shell execution, and no-auto-persistence boundary.
Human decision still required: No.

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

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.