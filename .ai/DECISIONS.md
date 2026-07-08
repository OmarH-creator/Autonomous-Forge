# Autonomous Decisions

## DEC-053 — 2026-07-08 — Expose validation-result audit as an installed command

Context: The repository already had a read-only validation-result audit helper for saved run-history observations, but users and CI could not invoke it through the installed `forge` console command before future patch or diff workflows begin.
Decision: Add an installed `forge validation-result-audit --record ... --root ... --format text|json` command through a small CLI entry-point extension that delegates all existing commands to the established CLI implementation. Add deterministic CLI tests and CI smoke coverage that writes a validation result, audits it, JSON-validates the output, and asserts a consistent guard.
Alternatives considered: Modify the large existing CLI file directly in the GitHub API-only environment, keep only programmatic usage, delay CLI exposure until patch generation, combine audit with validation-result writing, poll workflow status, infer success from saved fields, or make the audit mutating.
Consequences: The installed CLI now exposes a narrow read-only guard over saved validation observations while preserving existing command behavior and keeping validation execution, result persistence, audit, and future patch workflows separate.
Human decision still required: No.

## DEC-052 — 2026-07-08 — Audit saved validation observations before patch workflows

Context: The repository can now run one exact validation command, emit a persistence handoff, and persist reviewed executor output into a saved run-history record. Future patch or diff workflows need a read-only way to inspect whether those saved validation fields are internally consistent before relying on them.
Decision: Add a package-level `validation_result_audit` helper that reads one path-validated `.ai/run-history/*.json` record, reports `validation_execution`, `validation_result`, and `validation_note`, and returns `consistent` or `needs-review` guard notes without mutating files or inferring success.
Alternatives considered: Trust saved validation fields without a separate audit, rely only on run-history read/list output, expose a CLI before the package helper exists, poll workflow status, verify commits, inspect diffs, auto-approve records, or combine audit with patch generation.
Consequences: Future CLI and patch-adjacent surfaces can review saved validation observations through a narrow deterministic helper, while validation execution, persistence, audit, and any future implementation workflow remain separate.
Human decision still required: No.

## DEC-051 — 2026-07-08 — Exercise executor handoff persistence in CI

Context: CI already ran `forge executor-run --format json`, but the resulting JSON was written under `/tmp`, while `forge executor-handoff-persist` intentionally accepts only repository-local JSON paths. That meant the installed-package smoke path did not verify the guarded handoff persistence command.
Decision: Change the workflow to write executor output to repository-local `executor-run-output.json`, JSON-validate it, run `forge executor-handoff-persist --confirm-write --format json`, and assert that the executor handoff remains advisory/non-automatic while the persisted summary reports `external_result_attached` and `passed`.
Alternatives considered: Keep only unit tests, write executor output under `/tmp` and skip persistence, weaken the executor-output path guard to accept external paths, auto-persist from executor-run, or add a separate workflow job with duplicated setup.
Consequences: CI now exercises the complete installed executor-to-persistence handoff while preserving the repository-local path guard and the explicit separation between command execution and history mutation.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
