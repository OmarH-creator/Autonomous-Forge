# Autonomous Decisions

## DEC-054 — 2026-07-08 — Require regular files for run-history reads

Context: Run-history readers already rejected paths outside the repository root, paths outside `.ai/run-history/`, non-JSON extensions, missing files, directories, and direct symlinks. A remaining edge case allowed non-regular filesystem entries with a `.json` suffix to reach the JSON read step.
Decision: Require resolved run-history record paths to satisfy `Path.is_file()` after the existing symlink, directory, extension, existence, root, and history-directory checks. Add regression coverage for FIFO/non-regular record paths where the platform supports creating them.
Alternatives considered: Rely on JSON read errors, only keep the existing directory guard, add this guard only to validation-result audit, broaden the reader to scan directories, or defer filesystem hardening until patch workflows exist.
Consequences: Saved-record readers now have a clearer filesystem boundary before future executor-observation, patch, or diff workflows depend on durable run-history JSON records.
Human decision still required: No.

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

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
