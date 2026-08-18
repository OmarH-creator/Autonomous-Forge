# AUTO-164 — Refuse silent run-history overwrites

## Objective
Protect durable `.ai/run-history/` records from accidental replacement by making record paths immutable through the run-history writer.

## Repository and PR assessment
The run inspected README/docs, source/tests/config/CI, repository policy and autonomous memory, recent commits, open issues, all visible branches, and recent pull requests. Historical feature and maintenance branches remain stale or superseded by `main`. PR #8 identified this overwrite defect correctly, but its July branch is far behind current `main` and GitHub reports it non-mergeable, so the relevant behavior was integrated directly on `main` rather than merging stale code.

## Change
`write_run_history_record` now refuses any existing output path. The normal `--confirm-write` gate remains mandatory for a new record, and callers must select a different path for a later record. Focused tests cover refusal and preservation of existing content.

## Safety rationale
The default becomes more conservative. Existing run-history contents are preserved once the record path exists. Path containment, `.ai/run-history/` confinement, `.json` enforcement, preflight readiness, and write confirmation remain unchanged. No network access, command execution, Git mutation, workflow change, force push, or protection change is introduced.

## Validation
The changed writer and focused regression test syntax-compile successfully in the available scratch Python environment. Full local pytest remains unavailable because this runtime cannot clone the repository. Post-push repository CI is checked when observable and no green result is fabricated without evidence.

## Next action
If the final matrix is green, continue the integrated maintenance milestone. Prefer eliminating another caller-managed local handoff or addressing a concrete persistence/integrity defect over adding standalone read-only commands. External GitHub evidence acquisition remains policy-gated pending explicit approval.
