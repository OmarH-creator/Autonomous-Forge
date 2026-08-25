# AUTO-204 — Bound live workflow-status subprocess execution

## Objective

Close a concrete reliability and safety gap in the already-shipped opt-in live workflow-status collection path by bounding every external `git` and `gh` subprocess.

## Repository assessment

- `forge plan` and the integrated guarded-maintenance workflow are already shipped; this run stayed on that milestone rather than adding another read-only surface.
- README/docs, commit-status review, verified push orchestration, relevant tests, repository policy, CI, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history were inspected.
- The seven non-`main` branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration.
- Open issues #1, #6, and #9 are broader product/discussion requests rather than blockers for this bounded-execution defect.

## Rationale

AUTO-202/AUTO-203 integrated live GitHub workflow status into verified push orchestration and bound every returned workflow run to the verified commit. The collector limited the number of returned runs but its `subprocess.run` calls had no timeout. A hung local Git process or authenticated GitHub CLI could therefore stall the guarded maintenance workflow indefinitely, contradicting Forge's bounded-execution safety model.

## Work

- Added `_LIVE_COMMAND_TIMEOUT_SECONDS = 15` to `commit_status_review.py`.
- Applied that timeout to both text (`git rev-parse HEAD`) and JSON (`gh run list ...`) subprocess helpers.
- Converted `subprocess.TimeoutExpired` into a deterministic `CommitStatusReviewError` that stops live evidence collection fail closed.
- Updated the live collection safety boundary and command documentation to state the timeout explicitly.
- Updated deterministic tests so both live subprocess paths prove the timeout is supplied, and added a regression test proving timeout refusal.

## Validation

- Python syntax compilation passed for the changed implementation and focused test file in the available scratch environment.
- Focused executable smoke passed successful bounded Git/GitHub-CLI collection and fail-closed timeout handling.
- Product/test/doc head `b6d6ee0cacf3eabb3cfce0f1137589ecb9e29f8a` passed GitHub Actions run 32840874657 on Python 3.10, 3.11, and 3.12, including package installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest.
- Final README/state bookkeeping-head CI is inspected before the run is reported complete.

## Safety boundary

No new network surface, command type, workflow mutation, workflow rerun, push authority, force-push/tag-push behavior, remote mutation, branch-protection mutation, or permission change was added. The timeout only bounds external commands already executed by the explicit live-status capability; timeout errors stop before status review and push readiness.

## Limitations

- Live status still depends on installed/authenticated GitHub CLI.
- A timeout establishes only that collection exceeded 15 seconds, not the underlying cause.
- Workflow-run count remains capped at 20; subprocess output capture is not converted to a streaming byte-limited reader in this slice.
- Commit trust and branch-protection evidence remain caller-supplied.

## Next action

Continue the same integrated guarded-maintenance milestone with the next concrete cross-stage integrity defect or a policy-permitted evidence-handoff reduction. Do not add another standalone review command.