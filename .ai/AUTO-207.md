# AUTO-207 — Preserve live-status collection guarantees through status review

## Objective

Close the cross-stage integrity gap where bounded live GitHub workflow collection proved result completeness and exact per-run commit identity, but those guarantees were discarded when the raw collector payload became a commit-status review artifact used by higher-level push orchestration.

## Repository assessment

- `main` began at `0910eeddab8499fc277a9789a3a1e5ef2415d96a` (AUTO-206).
- AUTO-206 is green in Actions run 32888172331 across Python 3.10, 3.11, and 3.12.
- Inspected README/docs/examples, commit-status review implementation/tests, verified-push and push-readiness integration, repository policy/configured CI, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history.
- The seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration.
- Open issues #1, #6, and #9 remain broader product/discussion requests rather than blockers for the guarded-maintenance integrity milestone.

## Rationale

AUTO-205 and AUTO-206 established two live-collector guarantees before a workflow payload could be returned:

1. bounded completeness via the 20-run review limit plus a 21st sentinel query result; and
2. exact per-workflow-run binding to the requested commit SHA.

`build_commit_status_review_data()` previously retained the workflow states but dropped `workflow_run_limit`, `workflow_run_collection_complete`, and `workflow_run_commit_binding_complete`. Higher-level callers therefore received a clear status review without structured evidence that the live collector guarantees had survived the conversion boundary.

## Changes

- Added structured `live_collection_evidence` to live `gh run list` status reviews.
- Preserved the requested commit, configured workflow-run limit, bounded-completeness proof, and per-run commit-binding proof.
- Made live status review fail closed when the collection limit is invalid, completeness proof is absent, or commit-binding proof is absent.
- Kept supplied non-live status evidence backward compatible with `live_collection_evidence: null`.
- Added stable text rendering for the structured live-collection proof.
- Added deterministic focused coverage and updated command documentation plus README status.

## Safety

- No new external command type or network surface.
- No workflow rerun or workflow mutation.
- No patch, validation, commit, push, force-push, tag-push, remote, or branch-protection authority.
- Existing 15-second live `git`/`gh` timeouts and 20-run-plus-sentinel completeness checks remain unchanged.
- Repository policy allowed all changed paths under `src/**`, `tests/**`, `docs/**`, `README.md`, and `.ai/**`; prohibited workflow/secret paths were untouched.

## Validation

Deterministic AUTO-207 coverage verifies:

- successful live provenance retention;
- missing bounded-completeness proof blocks the review;
- missing per-run commit-binding proof blocks the review;
- invalid live collection limits block the review;
- supplied non-live status evidence remains backward compatible; and
- JSON/text output exposes the structured proof.

The substantive pushed head entered the repository's configured Python 3.10/3.11/3.12 Actions matrix. Final-head CI must be observed before a green completion claim.

## Limitations

- Live status still depends on installed/authenticated GitHub CLI.
- Commit trust and branch protection remain caller-supplied evidence.
- The structured live-collection proof now survives payload → status-review conversion, but push-readiness/handoff does not yet expose it as a dedicated top-level summary outside its nested evidence.
- Passing configured workflows still does not prove those workflows are sufficient for correctness.

## Next action

Inspect AUTO-207 final-head CI first. If green, carry the same structured live-status provenance into push-readiness/handoff evidence so the proof remains explicitly reviewable across the next integrated boundary without introducing a parallel evidence contract.
