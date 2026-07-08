# Autonomous Decisions

## DEC-056 — 2026-07-08 — Make executor-observation audit usable as a fail-closed gate

Context: `forge executor-observation-audit` can review aggregate saved executor observations, but before future patch-adjacent work it should also be usable as an explicit process gate rather than only an informational report.
Decision: Add `--require-clear` to `forge executor-observation-audit`. The command still prints the same read-only text or JSON audit, but returns a failing exit code unless the aggregate status is `clear`.
Alternatives considered: Keep the audit informational only, make all non-clear audits fail by default, persist gate decisions to history, poll workflow status, inspect diffs, verify commits, or infer validation success from saved fields.
Consequences: Maintainers and CI can now fail closed on blocked, missing, refused, or needs-review saved executor evidence before future patch or diff workflows rely on it, while the command remains read-only and non-authoritative.
Human decision still required: No.

## DEC-055 — 2026-07-08 — Audit aggregate saved executor observations before patch workflows

Context: The repository can now run one exact local validation command, persist reviewed executor-run JSON through guarded validation-result semantics, and audit one saved validation-result observation. Future patch or diff workflows need a broader read-only checkpoint that reviews all direct saved run-history records before relying on persisted executor evidence.
Decision: Add `executor_observation_audit` and expose it as `forge executor-observation-audit --root . --max-records 20 --format text|json`. The audit builds on the guarded run-history index, classifies each listed record as observed-clear, observed-blocked, missing-observation, needs-review, or refused, and reports a conservative aggregate status without mutating files or running validation.
Alternatives considered: Rely only on single-record validation-result audit, trust the run-history list validation guard, immediately inspect diffs, poll workflows, verify commits, generate patches, or make the audit mutating.
Consequences: Maintainers now have an aggregate saved-observation review surface before any patch-adjacent workflow is introduced, while validation execution, persistence, audit, patch generation, diff inspection, and policy enforcement remain separated.
Human decision still required: No.

## DEC-054 — 2026-07-08 — Require regular files for run-history reads

Context: Run-history readers already rejected paths outside the repository root, paths outside `.ai/run-history/`, non-JSON extensions, missing files, directories, and direct symlinks. A remaining edge case allowed non-regular filesystem entries with a `.json` suffix to reach the JSON read step.
Decision: Require resolved run-history record paths to satisfy `Path.is_file()` after the existing symlink, directory, extension, existence, root, and history-directory checks. Add regression coverage for FIFO/non-regular record paths where the platform supports creating them.
Alternatives considered: Rely on JSON read errors, only keep the existing directory guard, add this guard only to validation-result audit, broaden the reader to scan directories, or defer filesystem hardening until patch workflows exist.
Consequences: Saved-record readers now have a clearer filesystem boundary before future executor-observation, patch, or diff workflows depend on durable run-history JSON records.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
