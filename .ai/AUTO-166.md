# AUTO-166 — Make validation evidence single-assignment

## Objective
Close a concrete evidence-integrity gap in the durable maintenance workflow: `validation-result-write` could previously replace an already recorded validation outcome inside an existing run-history record after another confirmation.

## Repository and branch/PR assessment
The run inspected README/docs/examples, relevant source/tests/config/CI, repository policy, autonomous state, recent commits, open issues, all visible branches, and recent pull requests. Historical feature and maintenance branches remain stale or superseded by `main`; reviewed PRs are merged, closed, obsolete, or unrelated. No branch or PR was created or merged.

## Change
`build_validation_result_write_payload` now rejects a record when `validation_execution`, `validation_result`, or `validation_note` already contains non-empty evidence beyond the normal `none`/`not_run` placeholders. The normal first attachment remains supported. A contradictory retry or attempt to replace executor-produced validation raises `ValidationResultWriteError` before the record is rewritten.

## Tests
Focused deterministic coverage proves:

1. a successful first external attachment cannot be replaced by a contradictory second attachment; and
2. pre-existing executor validation cannot be replaced by an external attachment.

Both tests compare the complete record bytes before and after the refused mutation.

## Safety rationale
This is strictly more conservative than the previous behavior. Existing result validation, run-history path confinement, schema checks, context retention, and `--confirm-write` remain unchanged. No overwrite escape hatch, external command execution, network access, remote mutation, force-push, tag push, branch-protection change, or workflow change is introduced.

## Validation
The changed source module and focused regression test syntax-compile successfully in the available scratch Python environment. Full repository pytest is deferred to the repository's configured Python 3.10/3.11/3.12 CI when its push-triggered result becomes observable; no green result is claimed without evidence.

## Next action
Inspect AUTO-166 CI first. If green, continue the integrated end-to-end maintenance milestone with the next concrete persistence/provenance integrity defect or caller-managed evidence handoff reduction.
