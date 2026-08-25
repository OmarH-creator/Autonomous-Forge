# AUTO-206 — Bind live workflow rows to the requested commit inside the shared collector

## Inspection

Inspected current `main`, README/docs/examples, live commit-status and verified-push implementation/tests, configured CI, repository policy, autonomous roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, recent pull requests, and the final AUTO-205 Actions result. AUTO-205 is green in Actions run `32864546711`. The seven non-`main` branches remain historical/diverged and no reviewed PR contains newer applicable work. Open issues #1, #6, and #9 are broader product/discussion requests rather than blockers for the guarded-maintenance milestone.

## Objective and rationale

Close a cross-consumer evidence-integrity defect in the already-approved live GitHub workflow-status path. AUTO-203 required each workflow row to identify the verified created commit inside `verified-push-run`, but `collect_github_workflow_status_payload()` itself still trusted `gh run list --commit <sha>` to return correctly bound rows. Direct `forge commit-status-review --from-github` and any future collector consumer could therefore receive a payload labeled with the requested top-level SHA while an individual workflow row lacked or contradicted that identity.

## Change

- Require every admitted live workflow run to contain a non-empty `headSha`.
- Require every admitted `headSha` to equal the exact requested commit SHA before the row is normalized.
- Fail closed with an indexed diagnostic on missing or mismatched run identity.
- Record `workflow_run_commit_binding_complete=true` only on successful payloads.
- Preserve the existing 15-second subprocess timeout and one-row completeness sentinel beyond the 20-run review bound.
- Update direct live CLI regression fixtures so successful workflow rows carry the requested commit identity.

## Validation

Deterministic coverage was added for:

- successful collector-level commit binding and explicit completeness metadata;
- refusal of a workflow run belonging to a different commit;
- refusal of a workflow run with no head SHA;
- direct `commit-status-review --from-github` compatibility under the strengthened contract;
- unchanged timeout and truncation failure behavior.

The substantive implementation/test head has a push-triggered GitHub Actions run. Final-head CI is inspected before completion is reported; no green result is fabricated before that evidence is visible.

## Safety

This is hardening of an existing opt-in network surface, not a new external capability. It adds no new command type, workflow rerun, push authority, force-push/tag-push path, remote mutation, branch-protection mutation, or workflow permission. The collector remains bounded and metadata-only.

## Branch / PR disposition

Work stayed directly on `main`. No branch, pull request, merge request, merge, or force-push was created. Historical non-main branches remain inspect-only evidence.

## Visuals

No visual change was warranted because the maintenance lifecycle topology is unchanged; this change strengthens identity proof inside the existing live-status stage.

## Limitations

The collector proves that returned workflow rows belong to the requested commit and that no more than the configured bounded result window exists. It does not prove that the repository's configured workflow/check set is sufficient for correctness. Commit-trust and branch-protection evidence remain caller-supplied.

## Next action

Inspect AUTO-206 final-head CI first. Any failure takes priority. If green, continue the same integrated guarded-maintenance milestone with the next concrete cross-stage integrity defect or policy-permitted evidence-handoff reduction rather than adding another isolated read-only command.