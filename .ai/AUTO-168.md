# AUTO-168 — Make validation-result rename durability explicit

## Objective
Close the remaining crash-durability gap in AUTO-167's atomic validation-result attachment writer: flushing the temporary file before `os.replace` protects file contents, but durable rename semantics also require syncing the containing directory on filesystems that support it.

## Repository assessment
Inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits, open issues, TODO-oriented search, all visible branches, and recent pull requests. Historical branches remain stale or superseded by `main`; reviewed PRs are merged, closed, obsolete, or unrelated. No branch or PR was created or merged.

## Change
`validation_result_writer` now fsyncs the run-history directory immediately after the atomic replacement. Error reporting also distinguishes the two materially different failure boundaries: a failure before replacement still reports that the original record is preserved, while a directory-sync failure after replacement truthfully reports that the target was already replaced and instructs the caller to inspect it before retrying.

## Tests
Focused deterministic coverage verifies that a successful replacement performs both file and directory fsync, and that a simulated directory-sync failure does not falsely claim the original record survived after replacement.

## Safety rationale
This only strengthens persistence integrity. Existing explicit `--confirm-write`, path confinement, result/schema validation, single-assignment evidence, stale-source refusal, temporary-file cleanup, and atomic replacement remain unchanged. No network access, command execution, workflow mutation, force-push, tag push, remote mutation, or branch-protection change is introduced.

## Validation
The changed writer and focused AUTO-168 test syntax-compile successfully in the available scratch Python environment. Full Python 3.10/3.11/3.12 CI is inspected after publication when observable; no green result is claimed without evidence.

## Limitation and next action
Directory fsync is a durability improvement rather than a multi-process locking mechanism. The remaining design debt is the first-time in-place mutation of a durable run-history record; once AUTO-168 CI is green, the next highest-value persistence slice is an immutable, hash-bound validation attachment path with backward compatibility.
