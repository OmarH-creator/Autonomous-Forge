# AUTO-211 — Preserve live-status provenance in maintenance history links

## Inspection

- Inspected README/docs/examples, maintenance evidence/history-link code and tests, verified durable provenance, repository policy/CI, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history.
- Confirmed pre-run `main` at `000200093e5372b1dafd1820f84295291f88d80b` passed Actions run `32962092448`.
- The seven non-`main` branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration.

## Objective and rationale

AUTO-210 preserved normalized live workflow-status proof in the durable maintenance bundle, but the compact `.ai/run-history/` maintenance link did not expose that proof. AUTO-211 closes that evidence-continuity gap without creating another status-evidence contract.

## Change

- Added compact `live_status_evidence_summary` persistence to maintenance history links when durable `verified_provenance.live_status_evidence` is present.
- Revalidates `gh run list` source, exact bundle commit, workflow-run limit, bounded collection completeness, per-run commit binding, and the deterministic SHA-256 before linking.
- Added stable text rendering of the compact proof.
- Kept legacy/non-live bundles backward compatible with no synthetic summary.
- Added deterministic tests for successful persistence, digest tamper, commit drift, and legacy compatibility.
- Added `docs/HISTORY_LINK_LIVE_STATUS_PROVENANCE.md`.

## Safety

Evidence continuity only. This change adds no network or subprocess capability, workflow rerun, push authority, force-push/tag-push behavior, remote mutation, or branch-protection mutation. A malformed, incomplete, wrong-commit, or digest-drifted live proof fails closed before the history link is written.

## Validation

Focused deterministic tests are committed. AUTO-211 remains incomplete until the final Python 3.10/3.11/3.12 Actions matrix is observed and green.

## Next action

If CI is green, extend `maintenance-history-link-review --verify-linked-bundle` to verify and expose this same compact live-status summary against the linked durable bundle. Any CI failure takes priority.