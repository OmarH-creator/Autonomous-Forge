# AUTO-203 — Bind every live workflow run to the verified commit

## Objective

Close a cross-stage integrity gap in `forge verified-push-run --live-status`: the live collector was invoked for the verified commit SHA and the resulting review retained that top-level SHA, but individual workflow-run records were not independently required to identify the same commit.

## Repository assessment

- Started from `main` at `eb7020920ce5987063c2f971f8ea9558723ab275`.
- AUTO-202 final Actions run 32804378380 is green across Python 3.10, 3.11, and 3.12.
- Inspected README/docs, verified push/status/trust/commit implementation and tests, repository policy/configured CI, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history.
- The seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated; nothing warrants integration.
- Open issues #1, #6, and #9 remain broader product/discussion requests rather than blockers for the guarded-maintenance milestone.

## Change

`verified-push-run --live-status` now requires every returned workflow-run object to carry a non-empty `headSha`/normalized `head_sha` exactly equal to the verified created commit before the payload is converted into commit-status review evidence. A missing or mismatched run SHA fails closed before the status-review builder runs. The existing top-level review SHA equality check remains as a second binding check.

Deterministic tests cover:

- successful live status when the workflow run identifies the verified commit;
- refusal when a successful workflow run identifies another commit;
- refusal when a workflow run omits its head SHA;
- the existing pre-query gate for unverified commit evidence and primary CLI behavior.

## Safety and rationale

This is a strict integrity hardening of an already-shipped explicit live-status capability. It adds no network access, external-command authority, push authority, force-push/tag-push behavior, remote/protection mutation, workflow permission change, or workflow rerun capability. `--confirm-push` remains independent, and commit-trust plus branch-protection evidence remain caller-supplied.

## Validation

- Changed product source and focused regression tests syntax-compile successfully in the available scratch Python environment.
- Full repository validation is delegated to the existing push-triggered Actions matrix, which installs the package, compiles source, smoke-tests the installed CLI, validates the roadmap, and runs pytest on Python 3.10/3.11/3.12.
- The final workflow result must be inspected before AUTO-203 is reported complete.

## Visuals

None. This hardens evidence binding inside the existing push stage and does not alter lifecycle topology.

## Next action

If the final AUTO-203 matrix is green, continue the integrated guarded-maintenance milestone with the next concrete cross-stage integrity defect or policy-permitted evidence-handoff reduction rather than adding another isolated read-only command.
