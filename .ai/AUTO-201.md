# AUTO-201 — Restore the supported-version test baseline

## Objective

Repair the first observable red `main` workflow before taking new product work. AUTO-200's push-triggered test run completed with 30 failures and 1 error, so baseline recovery became the highest-priority blocker.

## Repository assessment

- Inspected README/docs, relevant source/tests/config/CI, repository policy, autonomous state/roadmap/changelog/decisions, recent commits, open issues, all eight visible branches, PR history, and fresh GitHub Actions runs.
- `forge plan` and the integrated guarded maintenance workflow are already shipped; this run therefore stayed on the existing end-to-end integrity milestone rather than opening a new standalone feature.
- The seven non-`main` branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated, and no branch/PR warranted integration.
- Open issues #1, #6, and #9 are broader product/discussion requests rather than blockers for the red baseline.

## Root cause and change

The largest failure cluster came from `validation_result_writer._refuse_existing_validation_result()`: immutable validation-result persistence recognized the newer placeholder `not_run` as empty, but historical `run-history/v1` records use the placeholder `not run`. Untouched legacy records were therefore misclassified as already containing validation evidence, cascading through validation attachments, replay, bundle provenance, and executor handoffs.

AUTO-201 now treats both placeholder spellings as equivalent empty states while continuing to refuse replacement of real validation evidence. The run also repaired three independent stale tests exposed by current contracts:

- corrected the AUTO-163 `capsys` fixture typo;
- expanded the AUTO-161 minimal policy fixture to include the currently required approval/validation sections;
- updated a verified-commit staged-drift test double for reviewed-parent `HEAD` capture;
- aligned the AUTO-170 sidecar expectation with the validation context the writer now deliberately retains.

## Validation

- AUTO-200 workflow run 32766735469 exposed the blocker: all three Python jobs reached pytest and failed; Python 3.11 reported 30 failed, 811 passed, 1 error.
- After the compatibility and stale-test repairs, workflow run 32789703818 reduced the suite to one stale expectation: Python 3.11 reported 1 failed, 841 passed.
- After correcting that final expectation, workflow run 32789756502 passed the pytest step on Python 3.10, 3.11, and 3.12. Installation, source compilation, installed CLI smoke tests, and roadmap validation also passed on those jobs.
- Final README/state/bookkeeping-head CI is inspected separately before the run is reported complete.

## Safety

- The immutability rule is not weakened for actual evidence: executor-produced results, prior external attachments, notes, and non-placeholder validation states remain single-assignment and fail closed.
- No workflow, secret, network, force-push, tag-push, remote, branch-protection, or external-command authority was added.
- Test changes align old fixtures with already-shipped product contracts rather than changing production behavior to satisfy stale assertions.
- Work remained directly on `main`; no branch or pull request was created or merged.

## Next action

After confirming the final AUTO-201 bookkeeping head is green, resume the existing guarded-maintenance milestone and choose the next concrete cross-stage integrity defect or meaningful evidence-handoff reduction rather than another isolated read-only surface.
